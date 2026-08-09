import os
import uuid
from datetime import date, datetime, timedelta
from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from celery.contrib.testing.worker import start_worker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from celery import current_app as current_celery_app
from src.common import get_db
from src.common.password_hash import pwd_hash
from src.common.security import create_access_token
from src.enums import TaskStatus
from src.main import fastapi_app
from src.models import PersonnelModel, RankerModel, TaskModel
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
def initialise_database():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="session")
def test_session() -> Generator[Session, None, None]:
    db_gen = get_db()
    db = next(db_gen)

    yield db

    db_gen.close()


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
# Clients
################################################################################


@pytest.fixture(scope="session")
def test_app():
    yield TestClient(fastapi_app, base_url="http://testserver/api/v1")


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
