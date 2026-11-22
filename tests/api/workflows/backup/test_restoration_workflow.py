import json
import shutil
import uuid
from json import JSONDecodeError
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock
from uuid import UUID
from zipfile import BadZipFile, ZipFile

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.script.revision import RangeNotAncestorError, ResolutionError
from pytest_mock import MockerFixture
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists, drop_database

from src.core import LinkedList
from src.core.database.db import temporary_db_session
from src.enums import BackupType
from src.schemas import BackupLink
from src.settings import app_config
from src.workflows import BackupRestorationWorkflow
from src.workflows.backup import restoration


INITIAL_REVISION = "6100399daf9f"
NEXT_REVISION = "a73d754c162c"
RANGED_METADATA = json.dumps({"database_alembic_version": INITIAL_REVISION})
INVALID_RANGED_ARCHIVES = {
    "missing_metadata_file": ({"dump.json": "{}"}, KeyError, "metadata.json"),
    "invalid_metadata_json": (
        {"metadata.json": "invalid", "dump.json": "{}"},
        JSONDecodeError,
        "Expecting value",
    ),
    "missing_schema_revision": (
        {"metadata.json": "{}", "dump.json": "{}"},
        ValueError,
        "Ranged backup has no schema revision",
    ),
    "missing_dump_file": ({"metadata.json": RANGED_METADATA}, KeyError, "dump.json"),
    "invalid_dump_json": (
        {"metadata.json": RANGED_METADATA, "dump.json": "invalid"},
        JSONDecodeError,
        "Expecting value",
    ),
}


def backup_link(backup_type: BackupType, path: Path = Path("backup.zip")) -> BackupLink:
    return BackupLink(
        model_id=uuid.uuid4(),
        parent_id=None,
        backup_type=backup_type,
        zip_file_path=path,
    )


def backup_chain(*backups: BackupLink) -> LinkedList:
    return LinkedList.create_from_ordered_list(ordered_list=list(backups))


def backup_archive(tmp_path: Path, files: dict[str, str]) -> Path:
    path = tmp_path / f"{uuid.uuid4()}.zip"

    with ZipFile(path, "w") as archive:
        for name, contents in files.items():
            archive.writestr(name, contents)

    return path


def select_ranged_backups(
    workflow: BackupRestorationWorkflow, *backups: BackupLink
) -> LinkedList:
    chain = backup_chain(backup_link(BackupType.LOGICAL), *backups)
    workflow.use_chain(chain)
    return chain


def current_revisions(database_name: str) -> tuple[str, ...]:
    with temporary_db_session(database_name) as session:
        return MigrationContext.configure(session.connection()).get_current_heads()


def ranged_person_archive(
    tmp_path: Path, revision: str, person_id: UUID, first_name: str
) -> Path:
    person = {"id": str(person_id), "first_name": first_name, "last_name": "Test"}
    return backup_archive(
        tmp_path,
        {
            "metadata.json": json.dumps({"database_alembic_version": revision}),
            "dump.json": json.dumps({"personal": [person]}),
        },
    )


def restored_first_name(database_name: str, person_id: UUID) -> str | None:
    with temporary_db_session(database_name) as session:
        return session.execute(
            text("SELECT first_name FROM personal WHERE id = :id"), {"id": person_id}
        ).scalar_one_or_none()


@pytest.fixture
def staging_database_name(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    name = f"test_restore_{uuid.uuid4().hex}"
    monkeypatch.setattr(app_config, "DATABASE_RESTORATION_DB_NAME", name)
    url = app_config.restoration_db_url

    try:
        yield name

    finally:
        if database_exists(url):
            drop_database(url)


@pytest.fixture
def staging_database(staging_database_name: str) -> str:
    create_database(app_config.restoration_db_url)

    return staging_database_name


@pytest.fixture
def switch_session(mocker: MockerFixture) -> MagicMock:
    session = mocker.patch.object(restoration, "temporary_db_session")

    return session.return_value.__enter__.return_value


class TestBackupRestorationWorkflow:
    def test_initial_state(self):
        test_backup_restoration_workflow = BackupRestorationWorkflow()

        assert test_backup_restoration_workflow.chain is None
        assert test_backup_restoration_workflow.selected_chain_node is None
        assert test_backup_restoration_workflow.restoration_database_created is False


class TestUseChainBackupRestorationWorkflow:
    def test_success_selects_first_node(
        self, test_backup_restoration_workflow: BackupRestorationWorkflow
    ):
        chain = backup_chain(
            backup_link(BackupType.LOGICAL), backup_link(BackupType.RANGED_DAY)
        )

        test_backup_restoration_workflow.use_chain(chain)

        assert test_backup_restoration_workflow.chain is chain
        assert (
            test_backup_restoration_workflow.selected_chain_node
            is chain.get_next_node()
        )

    def test_success_with_single_uploaded_backup(
        self, test_backup_restoration_workflow: BackupRestorationWorkflow
    ):
        uploaded = backup_link(BackupType.UPLOADED)
        chain = backup_chain(uploaded)

        test_backup_restoration_workflow.use_chain(chain)

        assert test_backup_restoration_workflow.selected_chain_node
        assert test_backup_restoration_workflow.selected_chain_node.item == uploaded

    def test_uploaded_backup_in_multi_node_chain(
        self, test_backup_restoration_workflow: BackupRestorationWorkflow
    ):
        chain = backup_chain(
            backup_link(BackupType.UPLOADED), backup_link(BackupType.RANGED_DAY)
        )

        with pytest.raises(
            ValueError, match="Uploaded backups must be restored by themselves"
        ):
            test_backup_restoration_workflow.use_chain(chain)


@pytest.mark.usefixtures("staging_database_name")
class TestRestoreLogicalBackupRestorationWorkflow:
    @pytest.mark.parametrize("backup_type", [BackupType.LOGICAL, BackupType.UPLOADED])
    def test_success(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        test_logical_backup_zip_name: Path,
        tmp_path: Path,
        staging_database_name: str,
        backup_type: BackupType,
    ):
        archive = tmp_path / "backup.zip"
        shutil.copyfile(test_logical_backup_zip_name, archive)

        test_backup_restoration_workflow.use_chain(
            backup_chain(backup_link(backup_type, archive))
        )

        test_backup_restoration_workflow.restore_new_database_to_logical_backup()

        assert test_backup_restoration_workflow.restoration_database_created
        assert current_revisions(staging_database_name) == ("100c57b4aae1",)

    def test_invalid_backup_type(
        self, test_backup_restoration_workflow: BackupRestorationWorkflow
    ):
        test_backup_restoration_workflow.use_chain(
            backup_chain(backup_link(BackupType.RANGED_DAY))
        )

        with pytest.raises(
            ValueError, match="Selected backup must be of type LOGICAL or UPLOADED"
        ):
            test_backup_restoration_workflow.restore_new_database_to_logical_backup()

    def test_invalid_archive(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        archive = tmp_path / "bad.zip"
        archive.write_text("not a ZIP")
        test_backup_restoration_workflow.use_chain(
            backup_chain(backup_link(BackupType.LOGICAL, archive))
        )

        with pytest.raises(BadZipFile):
            test_backup_restoration_workflow.restore_new_database_to_logical_backup()

    def test_missing_dump_in_archive(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        archive = backup_archive(tmp_path, {"metadata.json": "{}"})
        test_backup_restoration_workflow.use_chain(
            backup_chain(backup_link(BackupType.LOGICAL, archive))
        )

        with pytest.raises(StopIteration):
            test_backup_restoration_workflow.restore_new_database_to_logical_backup()

    @pytest.mark.usefixtures("staging_database")
    def test_staging_database_creation_failure(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        archive = backup_archive(tmp_path, {"database.dump": "backup contents"})
        test_backup_restoration_workflow.use_chain(
            backup_chain(backup_link(BackupType.LOGICAL, archive))
        )

        with pytest.raises(SystemError, match="Database already exists"):
            test_backup_restoration_workflow.restore_new_database_to_logical_backup()

        assert not test_backup_restoration_workflow.restoration_database_created

    def test_logical_restore_failure(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        archive = backup_archive(tmp_path, {"database.dump": "invalid dump"})
        test_backup_restoration_workflow.use_chain(
            backup_chain(backup_link(BackupType.LOGICAL, archive))
        )

        with pytest.raises(SystemError, match="Unable to restore database backup"):
            test_backup_restoration_workflow.restore_new_database_to_logical_backup()


class TestMigrateDatabaseBackupRestorationWorkflow:
    def test_success_to_head(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        head = ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()

        test_backup_restoration_workflow._migrate_restoration_database()

        assert current_revisions(staging_database) == (head,)

    def test_success_to_explicit_revision(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        test_backup_restoration_workflow._migrate_restoration_database(INITIAL_REVISION)

        test_backup_restoration_workflow._migrate_restoration_database(NEXT_REVISION)

        assert current_revisions(staging_database) == (NEXT_REVISION,)

    def test_success_when_already_at_target_revision(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        test_backup_restoration_workflow._migrate_restoration_database(INITIAL_REVISION)

        test_backup_restoration_workflow._migrate_restoration_database(INITIAL_REVISION)

        assert current_revisions(staging_database) == (INITIAL_REVISION,)

    def test_escapes_percent_signs_in_database_url(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        url = f"{app_config.restoration_db_url}?application_name=restore%20test"
        monkeypatch.setattr(
            type(app_config), "restoration_db_url", property(lambda _: url)
        )

        test_backup_restoration_workflow._migrate_restoration_database(INITIAL_REVISION)

        assert current_revisions(staging_database) == (INITIAL_REVISION,)

    def test_unknown_revision(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        with pytest.raises(ResolutionError, match="unknown-revision"):
            test_backup_restoration_workflow._migrate_restoration_database(
                "unknown-revision"
            )

        assert current_revisions(staging_database) == ()

    def test_downgrade_rejected(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        test_backup_restoration_workflow._migrate_restoration_database(NEXT_REVISION)

        with pytest.raises(RangeNotAncestorError):
            test_backup_restoration_workflow._migrate_restoration_database(
                INITIAL_REVISION
            )

        assert current_revisions(staging_database) == (NEXT_REVISION,)

    def test_migration_upgrade_failure(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        with temporary_db_session(staging_database) as session:
            session.execute(text("CREATE TABLE personal (id integer)"))
            session.commit()

        with pytest.raises(
            ProgrammingError, match='relation "personal" already exists'
        ):
            test_backup_restoration_workflow._migrate_restoration_database(
                INITIAL_REVISION
            )

        assert current_revisions(staging_database) == ()


class TestCreateDatabaseBackupRestorationWorkflow:
    def test_success_tracks_staging_database_ownership(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database_name: str,
    ):
        test_backup_restoration_workflow._create_restoration_database(
            staging_database_name
        )

        assert database_exists(app_config.restoration_db_url)
        assert test_backup_restoration_workflow.restoration_database_created

    def test_database_already_exists(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        with pytest.raises(SystemError, match="Database already exists"):
            test_backup_restoration_workflow._create_restoration_database(
                staging_database
            )

        assert database_exists(app_config.restoration_db_url)
        assert not test_backup_restoration_workflow.restoration_database_created

    def test_database_creation_failure(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database_name: str,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(app_config, "DATABASE_PORT", 65536)

        with pytest.raises(SystemError, match="Unable to create a new database"):
            test_backup_restoration_workflow._create_restoration_database(
                staging_database_name
            )

        assert not test_backup_restoration_workflow.restoration_database_created


class TestValidateDatabaseBackupRestorationWorkflow:
    def test_success_migrates_to_head(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        head = ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()

        test_backup_restoration_workflow.validate_restored_database()

        assert current_revisions(staging_database) == (head,)

    def test_migration_failure_propagates(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        with temporary_db_session(staging_database) as session:
            session.execute(text("CREATE TABLE personal (id integer)"))
            session.commit()

        with pytest.raises(
            ProgrammingError, match='relation "personal" already exists'
        ):
            test_backup_restoration_workflow.validate_restored_database()

    def test_table_validation_failure(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        staging_database: str,
    ):
        test_backup_restoration_workflow._migrate_restoration_database()

        with temporary_db_session(staging_database) as session:
            session.execute(text("DROP TABLE ranker"))
            session.commit()

        with pytest.raises(ProgrammingError, match='relation "ranker" does not exist'):
            test_backup_restoration_workflow.validate_restored_database()


class TestSwitchDatabaseBackupRestorationWorkflow:
    def test_success_renames_databases_and_returns_saved_name(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        switch_session: MagicMock,
    ):
        production = app_config.DATABASE_DB_NAME
        staging = app_config.DATABASE_RESTORATION_DB_NAME

        saved_name = (
            test_backup_restoration_workflow.switch_restored_database_into_service()
        )

        prefix = f"{production}_saved_"
        assert saved_name.startswith(prefix)
        assert saved_name.removeprefix(prefix).isdigit()

        statement, params = switch_session.execute.call_args.args
        save = f'ALTER DATABASE "{production}" RENAME TO "{saved_name}"'
        promote = f'ALTER DATABASE "{staging}" RENAME TO "{production}"'

        assert statement.text.index(save) < statement.text.index(promote)
        assert params == {"production": production, "restored": staging}

        switch_session.commit.assert_called_once_with()

    def test_database_identifiers_are_quoted(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        monkeypatch: pytest.MonkeyPatch,
        switch_session: MagicMock,
    ):
        monkeypatch.setattr(app_config, "DATABASE_DB_NAME", 'prod"db')
        monkeypatch.setattr(app_config, "DATABASE_RESTORATION_DB_NAME", 'stage"db')

        test_backup_restoration_workflow.switch_restored_database_into_service()

        statement, params = switch_session.execute.call_args.args
        assert 'ALTER DATABASE "prod""db" RENAME TO "prod""db_saved_' in statement.text
        assert 'ALTER DATABASE "stage""db" RENAME TO "prod""db"' in statement.text
        assert params == {"production": 'prod"db', "restored": 'stage"db'}

    def test_statement_failure_does_not_commit(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        switch_session: MagicMock,
    ):
        switch_session.execute.side_effect = SQLAlchemyError("Switch failed")

        with pytest.raises(SQLAlchemyError, match="Switch failed"):
            test_backup_restoration_workflow.switch_restored_database_into_service()

        switch_session.commit.assert_not_called()


@pytest.mark.usefixtures("staging_database_name")
class TestRestoreRangedBackupRestorationWorkflow:
    def test_success_with_no_ranged_backups(
        self, test_backup_restoration_workflow: BackupRestorationWorkflow
    ):
        chain = select_ranged_backups(test_backup_restoration_workflow)

        test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

        assert (
            test_backup_restoration_workflow.selected_chain_node
            is chain.get_next_node()
        )
        assert not database_exists(app_config.restoration_db_url)

    @pytest.mark.parametrize(
        "backup_type", [BackupType.RANGED_DAY, BackupType.RANGED_WEEK]
    )
    def test_success_with_ranged_backup(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
        staging_database: str,
        backup_type: BackupType,
    ):
        person_id = uuid.uuid4()
        archive = ranged_person_archive(
            tmp_path, INITIAL_REVISION, person_id, "Restored"
        )
        chain = select_ranged_backups(
            test_backup_restoration_workflow, backup_link(backup_type, archive)
        )

        test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

        assert restored_first_name(staging_database, person_id) == "Restored"
        assert current_revisions(staging_database) == (INITIAL_REVISION,)
        assert (
            test_backup_restoration_workflow.selected_chain_node
            is chain.get_ordered_list()[-1]
        )

    def test_restores_multiple_backups_in_chain_order(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
        staging_database: str,
    ):
        person_id = uuid.uuid4()
        first = ranged_person_archive(tmp_path, INITIAL_REVISION, person_id, "First")
        second = ranged_person_archive(tmp_path, NEXT_REVISION, person_id, "Second")
        chain = select_ranged_backups(
            test_backup_restoration_workflow,
            backup_link(BackupType.RANGED_DAY, first),
            backup_link(BackupType.RANGED_WEEK, second),
        )

        test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

        assert restored_first_name(staging_database, person_id) == "Second"
        assert current_revisions(staging_database) == (NEXT_REVISION,)
        assert (
            test_backup_restoration_workflow.selected_chain_node
            is chain.get_ordered_list()[-1]
        )

    def test_rejects_second_logical_backup(
        self, test_backup_restoration_workflow: BackupRestorationWorkflow
    ):
        select_ranged_backups(
            test_backup_restoration_workflow, backup_link(BackupType.LOGICAL)
        )

        with pytest.raises(SystemError, match="second logical backup"):
            test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

    @pytest.mark.parametrize(
        ("files", "error", "message"),
        INVALID_RANGED_ARCHIVES.values(),
        ids=tuple(INVALID_RANGED_ARCHIVES),
    )
    def test_invalid_ranged_archive(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
        files: dict[str, str],
        error: type[Exception],
        message: str,
    ):
        archive = backup_archive(tmp_path, files)
        select_ranged_backups(
            test_backup_restoration_workflow,
            backup_link(BackupType.RANGED_DAY, archive),
        )

        with pytest.raises(error, match=message):
            test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

    def test_migration_failure_does_not_apply_backup(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
        staging_database: str,
    ):
        test_backup_restoration_workflow._migrate_restoration_database(INITIAL_REVISION)
        person_id = uuid.uuid4()
        archive = ranged_person_archive(
            tmp_path, "unknown-revision", person_id, "Skipped"
        )

        select_ranged_backups(
            test_backup_restoration_workflow,
            backup_link(BackupType.RANGED_DAY, archive),
        )

        with pytest.raises(ResolutionError, match="unknown-revision"):
            test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

        assert restored_first_name(staging_database, person_id) is None

    @pytest.mark.usefixtures("staging_database")
    def test_apply_failure_does_not_advance_selected_node(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        archive = backup_archive(
            tmp_path,
            {"metadata.json": RANGED_METADATA, "dump.json": '{"missing_table": []}'},
        )
        chain = select_ranged_backups(
            test_backup_restoration_workflow,
            backup_link(BackupType.RANGED_DAY, archive),
        )

        with pytest.raises(ValueError, match="Unknown tables in ranged backup"):
            test_backup_restoration_workflow.fully_restore_logical_database_to_latest_ranged_backup()

        assert (
            test_backup_restoration_workflow.selected_chain_node
            is chain.get_next_node()
        )


class TestCleanupFolderBackupRestorationWorkflow:
    def test_success(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        folder = tmp_path / "restoration"
        folder.mkdir()
        (folder / "backup.dump").touch()

        test_backup_restoration_workflow.cleanup_folder(folder)

        assert not folder.exists()

    def test_folder_not_found(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        tmp_path: Path,
    ):
        folder = tmp_path / "missing"

        test_backup_restoration_workflow.cleanup_folder(folder)

        assert not folder.exists()

    def test_unexpected_error_logged(
        self,
        test_backup_restoration_workflow: BackupRestorationWorkflow,
        mocker: MockerFixture,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ):
        mocker.patch.object(restoration, "delete_folder", side_effect=PermissionError)

        test_backup_restoration_workflow.cleanup_folder(tmp_path / "restoration")

        assert "Unknown error whilst trying to clean up" in caplog.text
