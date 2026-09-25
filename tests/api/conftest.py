import os
import time
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import boto3
import pytest
from alembic import command
from alembic.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from celery.contrib.testing.worker import start_worker
from fastapi.testclient import TestClient
from pytest import TempPathFactory
from pytest_mock import MockerFixture
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from testcontainers.core.container import DockerContainer

from celery import current_app as current_celery_app
from src.common.security import create_access_token
from src.common.utils import utcnow
from src.core import get_backup_db, get_db
from src.core.password_hash import pwd_hash
from src.core.s3_storage import (
    ObjectStorage,
    get_object_storage_service,
)
from src.enums import BackupStatus, BackupTriggerMethod, BackupType, TaskStatus
from src.enums.object_type import ObjectType
from src.main import fastapi_app
from src.models import BackupModel, MetaModel, PersonnelModel, RankerModel, TaskModel
from src.schemas import (
    Metadata,
    MetadataData,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.schemas.backup import MetadataChecksum
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
def test_backup_zip_stored(
    test_backup_session: Session, test_object_storage: ObjectStorage
) -> Generator[BackupModel, None, None]:
    with open("/api/tests/files/20260925080016-tracker-backup.zip", "rb") as f:
        filename = "20260925080016-tracker-backup.zip"
        test_object_storage.upload_file(f, ObjectType.BACKUP, filename)

    backup_model = BackupModel(
        celery_id=uuid.uuid4(),
        trigger_method=BackupTriggerMethod.MANUAL,
        status=BackupStatus.SUCCESS,
        backup_type=BackupType.LOGICAL,
        duration=10.0,
        error_message=None,
        error_traceback=None,
    )
    test_backup_session.add(backup_model)
    test_backup_session.flush([backup_model])

    metadata = Metadata(
        backup_id=str(backup_model.id),
        backup_type=BackupType.LOGICAL,
        created_at=utcnow(),
        database_alembic_version="00000000",
        app_version=app_config.APP_VERSION,
        tool=MetadataTool(name="pg_dump", version="17.11"),
        files=[
            MetadataFiles(
                name="tracker-backup-2026-Sep-25.dump",
                type="backup",
                size_bytes=6000,
                checksum=MetadataChecksum(
                    algorithm="sha256",
                    value="711e725775090c79aad4d1d84f917ab2cf1e5e669506523903b6baf361b71362",
                    verified=True,
                    last_verified=utcnow(),
                ),
            )
        ],
        data=MetadataData(date_range=MetadataDateRange(start=utcnow(), end=utcnow())),
    )

    file_metadata = test_object_storage.file_metadata(ObjectType.BACKUP, filename)
    metadata_model = MetaModel(metadata, file_metadata)

    test_backup_session.add(metadata_model)
    test_backup_session.commit()

    yield backup_model

    test_backup_session.delete(backup_model)
    test_backup_session.commit()


################################################################################
# Celery Tasks
################################################################################


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


@pytest.fixture(scope="session", autouse=True)
def test_s3_container() -> Generator[None, None, None]:
    with (
        DockerContainer(
            "rustfs/rustfs:1.0.0"  # Ensure this version is up to date with dev/prod
        )
        .with_exposed_ports(9000)
        .with_env("RUSTFS_ADDRESS", ":9000")
        .with_env("RUSTFS_ACCESS_KEY", app_config.S3_ACCESS_KEY)
        .with_env("RUSTFS_SECRET_KEY", app_config.S3_SECRET_KEY)
    ) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(9000)
        endpoint = f"http://{host}:{port}"

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=app_config.S3_ACCESS_KEY,
            aws_secret_access_key=app_config.S3_SECRET_KEY,
            region_name=app_config.S3_REGION,
        )

        deadline = time.monotonic() + 30

        while True:
            try:
                client.list_buckets()
                break

            except (BotoCoreError, ClientError):
                if time.monotonic() > deadline:
                    raise

                time.sleep(0.5)

        app_config.S3_HTTP_ADDRESS = endpoint

        yield


################################################################################
# Clients
################################################################################


@pytest.fixture(scope="session")
def test_app(
    test_session: Session,
    test_backup_session: Session,
    test_object_storage: ObjectStorage,
):
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

    def _get_object_storage_service():
        try:
            yield test_object_storage
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = _get_test_db
    fastapi_app.dependency_overrides[get_backup_db] = _get_test_backup_db
    fastapi_app.dependency_overrides[get_object_storage_service] = (
        _get_object_storage_service
    )

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


@pytest.fixture(scope="session")
def test_session_admin(test_session: Session):
    model = PersonnelModel(
        email="admin@email.com",
        password=pwd_hash.hash(VALID_PASSWORD),
        first_name="Session",
        last_name="User",
    )
    model.is_admin = True

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


@pytest.fixture
def test_client_admin_session(test_app: TestClient, test_session_admin: PersonnelModel):
    test_app.headers.update(
        {"Authorization": f"Bearer {create_access_token(test_session_admin.id)}"}
    )

    yield test_app

    test_app.headers.pop("Authorization", None)


@pytest.fixture(scope="session")
def test_object_storage(test_s3_container: None):
    yield ObjectStorage()


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
