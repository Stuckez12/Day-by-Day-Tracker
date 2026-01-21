import os
import pytest

from alembic import command
from alembic.config import Config
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from types import SimpleNamespace
from typing import Generator


from backend.main import app
from backend.common import get_db
from backend.common.dependencies import get_personal_service
from backend.models import PersonalModel, RankerModel
from backend.services import PersonalService, RankingService


from tests.backend.constants import INVALID_PERSONNEL_ID


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
    test_client_v1.put(f"/personal/select", json={"id": str(test_personnel.id)})


@pytest.fixture
def test_set_cookies_invalid_user(test_client_v1_mocked_personnel_service: TestClient):
    test_client_v1_mocked_personnel_service.put(
        f"/personal/select", json={"id": INVALID_PERSONNEL_ID}
    )


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
