import os
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Generator
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from alembic import command
from alembic.config import Config
from celery.contrib.testing.worker import start_worker
from fastapi.testclient import TestClient
from pytest import TempPathFactory
from pytest_mock import MockerFixture
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from celery import current_app as current_celery_app
from src.common.security import create_access_token
from src.core import get_backup_db, get_db
from src.core.password_hash import pwd_hash
from src.enums import BackupStatus, BackupTriggerMethod, BackupType, TaskStatus
from src.main import fastapi_app
from src.models import BackupModel, MetaModel, PersonnelModel, RankerModel, TaskModel
from src.schemas import (
    Metadata,
    MetadataChecksum,
    MetadataData,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.services import (
    AuthService,
    BackupService,
    PersonnelService,
    RankingService,
    TaskService,
)
from src.settings import app_config
from tests.api.constants import VALID_PASSWORD


################################################################################
# Misc
################################################################################


@pytest.fixture(scope="session", autouse=True)
def check_testing_environment():
    assert os.getenv("APP_ENV") == "test"


@pytest.fixture(scope="session", autouse=True)
def test_engine() -> Generator[Engine, None, None]:
    engine = create_engine(app_config.db_url)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", app_config.db_url)

    if not database_exists(app_config.db_url):
        create_database(app_config.db_url)

    command.upgrade(alembic_cfg, "head")

    yield engine

    command.downgrade(alembic_cfg, "base")
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_backup_engine() -> Generator[Engine, None, None]:
    engine = create_engine(app_config.backup_db_url)
    alembic_cfg = Config("alembic-backup.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", app_config.backup_db_url)

    if not database_exists(app_config.backup_db_url):
        create_database(app_config.backup_db_url)

    command.upgrade(alembic_cfg, "head")

    yield engine

    command.downgrade(alembic_cfg, "base")
    engine.dispose()


@pytest.fixture(scope="session")
def test_session(test_engine: Engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def test_backup_session(test_backup_engine: Engine) -> Generator[Session, None, None]:
    connection = test_backup_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_backup_engine
    )
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def test_date_today() -> Generator[date, None, None]:
    yield date.today()


@pytest.fixture(scope="session")
def celery_app():
    celery_app = current_celery_app
    celery_app.config_from_object(app_config, namespace="CELERY")

    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

    yield celery_app


@pytest.fixture(scope="session")
def celery_worker(celery_app, shared_tmp_path):
    celery_app.conf.update(
        SHARED_STORAGE_PATH=str(shared_tmp_path),
    )
    with start_worker(celery_app, perform_ping_check=False):
        yield None


@pytest.fixture(scope="function")
def test_temp_backup_path(mocker: MockerFixture, tmp_path: Path):
    mocker.patch.object(app_config, "BACKUP_PATH", str(tmp_path))

    yield tmp_path


################################################################################
# Test Files
################################################################################


@pytest.fixture(scope="session")
def shared_tmp_path(tmp_path_factory: TempPathFactory):
    return tmp_path_factory.mktemp("shared")


@pytest.fixture(scope="function")
def test_file(tmp_path: Path):
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"hello world")

    return test_file


@pytest.fixture(scope="function")
def test_backup_zip(shared_tmp_path: Path, test_metadata_schema: Metadata):
    zip_temp_path = shared_tmp_path / "zip_creation"
    Path(zip_temp_path).mkdir()

    backup_file = zip_temp_path / "backup.sql"
    backup_file.write_bytes(b"INSERT INTO help (id) VALUES (1);")

    checksum_file = zip_temp_path / "backup.checksum"
    checksum_file.write_bytes(
        b"3c8988be5542abfd6dcbd716f1574dbc779d90feebaa54151934a56eeb98a38a"
    )

    # Modify metadata to point to newly created test files
    test_metadata_schema.files = [
        MetadataFiles(
            name=backup_file.name, type="backup", size_bytes=backup_file.stat().st_size
        ),
        MetadataFiles(
            name=checksum_file.name,
            type="checksum",
            size_bytes=checksum_file.stat().st_size,
        ),
    ]

    metadata_file = zip_temp_path / "metadata.json"
    metadata_file.write_bytes(test_metadata_schema.model_dump_json().encode())

    # Zip
    files = [backup_file, metadata_file, checksum_file]

    zip_file = shared_tmp_path / "backup.zip"

    with ZipFile(zip_file, "w", compression=ZIP_DEFLATED) as zf:
        for file in files:
            path = Path(file)
            zf.write(path, arcname=path.name)

    yield zip_file.name

    Path(zip_file).unlink()
    Path(checksum_file).unlink()
    Path(metadata_file).unlink()
    Path(backup_file).unlink()
    Path(zip_temp_path).rmdir()


################################################################################
# Celery Tasks
################################################################################


@pytest.fixture
def mock_task_db(test_session: Session, test_backup_session: Session):
    def _get_test_db():
        yield test_session

    def _get_test_backup_db():
        yield test_backup_session

    with (
        patch("src.core.get_db", _get_test_db),
        patch("src.core.get_backup_db", _get_test_backup_db),
    ):
        yield


################################################################################
# Clients
################################################################################


@pytest.fixture(scope="session")
def test_app(test_session: Session, test_backup_session: Session):
    def _get_test_db():
        try:
            yield test_session
        finally:
            pass

    def _get_test_backup_db():
        try:
            yield test_backup_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = _get_test_db
    fastapi_app.dependency_overrides[get_backup_db] = _get_test_backup_db

    with TestClient(fastapi_app, base_url="http://testserver/api/v1") as client:
        yield client


@pytest.fixture
def test_client_user(test_app: TestClient, test_personnel: PersonnelModel):
    test_app.headers.update(
        {"Authorization": f"Bearer {create_access_token(test_personnel.id)}"}
    )

    yield test_app

    test_app.headers.pop("Authorization", None)


@pytest.fixture(scope="session")
def test_session_personnel(test_session: Session):
    model = PersonnelModel(
        email="session@email.com",
        password=pwd_hash.hash(VALID_PASSWORD),
        first_name="Session",
        last_name="User",
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture
def test_client_user_session(
    test_app: TestClient, test_session_personnel: PersonnelModel
):
    test_app.headers.update(
        {"Authorization": f"Bearer {create_access_token(test_session_personnel.id)}"}
    )

    yield test_app

    test_app.headers.pop("Authorization", None)


################################################################################
# Schemas
################################################################################


@pytest.fixture(scope="function")
def test_metadata_schema(test_backup: BackupModel):
    yield Metadata(
        backup_id=str(test_backup.id),
        backup_type=BackupType.LOGICAL,
        created_at=datetime.now(),
        database_alembic_version="qwertyuiop",
        app_version="1.0.0",
        checksum=MetadataChecksum(
            algorithm="SHA256",
            file_name="test_zip",
            verified=True,
            last_verified=datetime.now(),
        ),
        tool=MetadataTool(
            name="pg_dump",
            version="17.1",
        ),
        files=[MetadataFiles(name="test_file_name", type="backup", size_bytes=1)],
        data=MetadataData(
            date_range=MetadataDateRange(start=datetime.now(), end=datetime.now())
        ),
    )


################################################################################
# Services
################################################################################


@pytest.fixture(scope="function")
def test_auth_service(test_session: Session):
    yield AuthService(db=test_session)


@pytest.fixture(scope="function")
def test_backup_service(
    mocker: MockerFixture,
    tmp_path: Path,
    test_session: Session,
    test_backup_session: Session,
):
    mocker.patch.object(
        app_config,
        "BACKUP_PATH",
        str(tmp_path),
    )
    yield BackupService(db=test_session, backup_db=test_backup_session)


@pytest.fixture(scope="function")
def test_personnel_service(test_session: Session):
    yield PersonnelService(db=test_session)


@pytest.fixture(scope="function")
def test_ranking_service(test_session: Session):
    yield RankingService(db=test_session)


@pytest.fixture(scope="function")
def test_task_service(test_session: Session):
    yield TaskService(db=test_session)


################################################################################
# Models
################################################################################


@pytest.fixture(scope="function")
def test_personnel(test_session: Session):
    model = PersonnelModel(
        email="email@email.com",
        password=pwd_hash.hash(VALID_PASSWORD),
        first_name="Test",
        last_name="Fixture",
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_personnel_2(test_session: Session):
    model = PersonnelModel(
        email="email2@email.com",
        password=pwd_hash.hash(VALID_PASSWORD),
        first_name="Test 2",
        last_name="Fixture 2",
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_personnel_3(test_session: Session):
    model = PersonnelModel(
        email="email3@email.com",
        password=pwd_hash.hash(VALID_PASSWORD),
        first_name="Test 3",
        last_name="Fixture 3",
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_ranker(
    test_session: Session, test_date_today: date, test_session_personnel: PersonnelModel
):
    model = RankerModel(
        personnel_id=test_session_personnel.id,
        day=test_date_today,
        ranking=5,
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_ranker_set_date(test_session: Session, test_session_personnel: PersonnelModel):
    model = RankerModel(
        personnel_id=test_session_personnel.id,
        day=date(2000, 1, 1),
        ranking=10,
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_ranker_none(
    test_session: Session, test_date_today: date, test_session_personnel: PersonnelModel
):
    model = RankerModel(
        personnel_id=test_session_personnel.id,
        day=test_date_today,
        ranking=None,
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_task_1(test_session: Session):
    model = TaskModel(
        task_id=uuid.uuid4(),
        name="task1",
        status=TaskStatus.PENDING,
    )

    model.retries = 0
    model.started_at = datetime.now()
    model.ended_at = datetime.now() + timedelta(seconds=60)
    model.error = "error message"

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_task_2(test_session: Session):
    model = TaskModel(
        task_id=uuid.uuid4(),
        name="task2",
        status=TaskStatus.RUNNING,
    )

    model.retries = 2
    model.started_at = datetime.now() + timedelta(seconds=10)
    model.ended_at = datetime.now() + timedelta(seconds=30)
    model.error = "error message"

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_task_3(test_session: Session):
    model = TaskModel(
        task_id=uuid.uuid4(),
        name="task2",
        status=TaskStatus.SUCCESS,
    )

    model.retries = 1
    model.started_at = datetime.now()
    model.ended_at = datetime.now() + timedelta(seconds=40)
    model.error = "error message"

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_backup(test_backup_session: Session):
    model = BackupModel(
        celery_id=uuid.uuid4(),
        trigger_method=BackupTriggerMethod.MANUAL,
        status=BackupStatus.SUCCESS,
        backup_type=BackupType.LOGICAL,
        duration=10.0,
        error_message=None,
        error_traceback=None,
    )

    test_backup_session.add(model)
    test_backup_session.commit()

    yield model

    test_backup_session.delete(model)
    test_backup_session.commit()


@pytest.fixture(scope="function")
def test_backup_2(test_backup_session: Session):
    model = BackupModel(
        celery_id=uuid.uuid4(),
        trigger_method=BackupTriggerMethod.SCHEDULED,
        status=BackupStatus.SUCCESS,
        backup_type=BackupType.LOGICAL,
        duration=10.0,
        error_message=None,
        error_traceback=None,
    )

    test_backup_session.add(model)
    test_backup_session.commit()

    yield model

    test_backup_session.delete(model)
    test_backup_session.commit()


@pytest.fixture(scope="function")
def test_backup_w_file(
    test_temp_backup_path: Path,
    test_backup_session: Session,
    test_metadata: MetaModel,
):
    test_file = test_temp_backup_path / "test.txt"
    test_file.write_bytes(b"hello world")

    test_metadata.zip_filename = test_file.name
    test_metadata.zip_path = f"/{test_file.name}"
    test_metadata.zip_size_bytes = test_file.stat().st_size

    test_backup_session.commit()

    yield test_file


@pytest.fixture(scope="function")
def test_metadata(test_backup_session: Session, test_metadata_schema: Metadata):
    model = MetaModel(metadata_schema=test_metadata_schema, zipped_backup_path="/")

    test_backup_session.add(model)
    test_backup_session.commit()

    yield model

    test_backup_session.delete(model)
    test_backup_session.commit()
