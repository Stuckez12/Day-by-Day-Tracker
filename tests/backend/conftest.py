import os
import pytest

from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session
from typing import Generator

from backend.common import get_db
from backend.services import PersonalService


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


@pytest.fixture(scope="function")
def test_personal_service(test_session: Session):
    yield PersonalService(db=test_session)
