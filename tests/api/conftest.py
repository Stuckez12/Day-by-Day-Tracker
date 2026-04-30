import os
import pytest
import uuid

from alembic import command
from alembic.config import Config
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import Generator

from src.common import get_db
from src.common.password_hash import pwd_hash
from src.main import app
from src.models import PersonalModel, RankerModel
from src.services import AuthService, PersonalService, RankingService

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


@pytest.fixture(scope="function")
def test_session() -> Generator[Session, None, None]:
    db_gen = get_db()
    db = next(db_gen)

    yield db

    db_gen.close()


@pytest.fixture
def test_set_cookies(test_client_v1: TestClient, test_personnel: PersonalModel):
    response = test_client_v1.post(
        "/auth/login",
        json={"email": test_personnel.email, "password": VALID_PASSWORD},
    )
    assert response.status_code == 204

    yield

    test_client_v1.cookies.pop("personnel_id", None)


@pytest.fixture
def test_set_invalid_cookies(test_client_v1: TestClient):
    id = str(uuid.uuid4())
    test_client_v1.cookies.set("personnel_id", id)

    yield id

    test_client_v1.cookies.pop("personnel_id", None)


@pytest.fixture(scope="session")
def test_date_today() -> Generator[date, None, None]:
    yield date.today()


################################################################################
# Clients
################################################################################


@pytest.fixture(scope="function")
def test_client_v1():
    yield TestClient(app, base_url="http://testserver/api/v1")


################################################################################
# Services
################################################################################


@pytest.fixture(scope="function")
def test_auth_service(test_session: Session):
    yield AuthService(db=test_session)


@pytest.fixture(scope="function")
def test_personal_service(test_session: Session):
    yield PersonalService(db=test_session)


@pytest.fixture(scope="function")
def test_ranking_service(test_session: Session):
    yield RankingService(db=test_session)


################################################################################
# Models
################################################################################


@pytest.fixture(scope="function")
def test_personnel(test_session: Session):
    model = PersonalModel(
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
    model = PersonalModel(
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
    model = PersonalModel(
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
    test_session: Session, test_date_today: date, test_personnel: PersonalModel
):
    model = RankerModel(
        personal_id=test_personnel.id,
        day=test_date_today,
        ranking=5,
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()


@pytest.fixture(scope="function")
def test_ranker_set_date(test_session: Session, test_personnel: PersonalModel):
    model = RankerModel(
        personal_id=test_personnel.id,
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
    test_session: Session, test_date_today: date, test_personnel: PersonalModel
):
    model = RankerModel(
        personal_id=test_personnel.id,
        day=test_date_today,
        ranking=None,
    )

    test_session.add(model)
    test_session.commit()

    yield model

    test_session.delete(model)
    test_session.commit()
