from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.exc import NoResultFound

from src.models import BackupModel
from src.schemas import ApplicationSettingsSchema
from src.services import BackupService
from src.tasks import database_restoration
from src.workflows import BackupRestorationWorkflow


TASK_MODULE = "src.tasks.maintenance.database_restoration"


@pytest.fixture
def restoration_path(
    mocker: MockerFixture,
    test_app_settings: ApplicationSettingsSchema,
    tmp_path: Path,
):
    mocker.patch(
        f"{TASK_MODULE}.get_configurable_application_settings",
        return_value=test_app_settings,
    )
    path = tmp_path / "restoration"
    mocker.patch(f"{TASK_MODULE}.TEMP_RESTORATION_PATH", path)

    return path


@pytest.fixture
def mock_restore_backup(
    mocker: MockerFixture, test_backup: BackupModel, restoration_path: Path
):
    mocker.patch.object(BackupService, "get_by_backup_id", return_value=test_backup)
    mocker.patch.object(
        BackupService, "retrieve_zip_file", return_value=restoration_path / "backup.zip"
    )


@pytest.mark.usefixtures("mock_task_db", "celery_worker", "restoration_path")
class TestDatabaseRestorationTask:
    def test_backup_not_found(self, mocker: MockerFixture):
        mocker.patch.object(
            BackupService, "get_by_backup_id", side_effect=NoResultFound
        )

        with pytest.raises(ValueError, match="Backup provided does not exist"):
            database_restoration.apply_async()

    def test_preparation_failure_is_reraised(
        self, mocker: MockerFixture, restoration_path: Path
    ):
        mocker.patch.object(
            BackupService,
            "get_by_backup_id",
            side_effect=RuntimeError("Backup lookup failed"),
        )

        with pytest.raises(RuntimeError, match="Backup lookup failed"):
            database_restoration.apply_async()

        assert not restoration_path.exists()

    @pytest.mark.usefixtures("mock_restore_backup")
    def test_workflow_failure_is_reraised(
        self, mocker: MockerFixture, restoration_path: Path
    ):
        mocker.patch.object(
            BackupRestorationWorkflow,
            "restore_new_database_to_logical_backup",
            side_effect=RuntimeError("Restore failed"),
        )

        with pytest.raises(RuntimeError, match="Restore failed"):
            database_restoration.apply_async()

        assert not restoration_path.exists()

    @pytest.mark.usefixtures("mock_restore_backup")
    def test_database_cleanup_failure_preserves_original_error(
        self, mocker: MockerFixture
    ):
        def fail_restore(workflow: BackupRestorationWorkflow):
            workflow.restoration_database_created = True
            raise RuntimeError("Restore failed")

        mocker.patch.object(
            BackupRestorationWorkflow,
            "restore_new_database_to_logical_backup",
            autospec=True,
            side_effect=fail_restore,
        )

        mocker.patch(f"{TASK_MODULE}.database_exists", return_value=True)
        drop_database = mocker.patch(
            f"{TASK_MODULE}.drop_database", side_effect=RuntimeError("Cleanup failed")
        )

        with pytest.raises(RuntimeError, match="Restore failed"):
            database_restoration.apply_async()

        drop_database.assert_called_once()
