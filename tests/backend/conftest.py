import os
import pytest

from alembic import command
from alembic.config import Config
from datetime import date
from sqlalchemy.orm import Session
from typing import Generator

from backend.common import get_db
from backend.models import PersonalModel, RankerModel
from backend.services import PersonalService, RankingService


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


@pytest.fixture(scope="session")
def test_date_today() -> Generator[date, None, None]:
    yield date.today()


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
