import os
import uuid
from datetime import date, datetime, timedelta
from typing import Generator
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from celery.contrib.testing.worker import start_worker
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from celery import current_app as current_celery_app
from src.common import get_backup_db, get_db
from src.common.password_hash import pwd_hash
from src.common.security import create_access_token
from src.enums import TaskStatus
from src.enums.backup.status import BackupStatus
from src.enums.backup.trigger_method import BackupTriggerMethod
from src.enums.backup.type import BackupType
from src.main import fastapi_app
from src.models import BackupModel, MetaModel, PersonnelModel, RankerModel, TaskModel
from src.schemas.backup import (
    Metadata,
    MetadataChecksum,
    MetadataData,
    MetadataDateRange,
    MetadataFiles,
    MetadataTool,
)
from src.services import AuthService, PersonnelService, RankingService, TaskService
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
def celery_worker(celery_app):
    with start_worker(celery_app, perform_ping_check=False):
        yield None


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
        patch("src.common.get_db", _get_test_db),
        patch("src.common.get_backup_db", _get_test_backup_db),
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
def test_metadata(test_backup_session: Session, test_metadata_schema: Metadata):
    model = MetaModel(metadata_schema=test_metadata_schema, zipped_backup_path="/")

    test_backup_session.add(model)
    test_backup_session.commit()

    yield model

    test_backup_session.delete(model)
    test_backup_session.commit()
