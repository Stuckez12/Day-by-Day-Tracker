import pytest

from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import PersonalModel
from src.schemas import CreatePersonnelRequest, LogInRequest
from src.services import AuthService

from tests.api.constants import VALID_PASSWORD


class TestAuthService:
    def test_register_personnel(
        self, test_session: Session, test_auth_service: AuthService
    ):
        data = CreatePersonnelRequest(
            email="email@email.com",
            password="Password1.",
            first_name="Test",
            last_name="User",
        )

        personnel = test_auth_service.register(data)

        try:
            assert personnel.email == data.email
            assert personnel.password == data.password
            assert personnel.first_name == data.first_name
            assert personnel.last_name == data.last_name

        finally:
            test_session.delete(personnel)
            test_session.commit()

    def test_register_personnel_email_already_in_use(
        self, test_auth_service: AuthService, test_personnel: PersonalModel
    ):
        data = CreatePersonnelRequest(
            email=test_personnel.email,
            password="Password1.",
            first_name="Test",
            last_name="User",
        )

        with pytest.raises(ValueError, match="Email already in use"):
            test_auth_service.register(data)

    def test_register_personnel_password_hashing_fails(
        self, mocker: MockerFixture, test_auth_service: AuthService
    ):
        mocker.patch.object(pwd_hash, "hash", side_effect=ValueError("Forced Error"))

        data = CreatePersonnelRequest(
            email="email@email.com",
            password="Password1.",
            first_name="Test",
            last_name="User",
        )

        with pytest.raises(
            ValueError, match="Unable to hash password. Please try again"
        ):
            test_auth_service.register(data)

    def test_log_in_personnel(
        self, test_auth_service: AuthService, test_personnel: PersonalModel
    ):
        data = LogInRequest(
            email=test_personnel.email,
            password=VALID_PASSWORD,
        )

        result = test_auth_service.log_in(data)
        assert result == test_personnel

    def test_log_in_personnel_invalid_email(self, test_auth_service: AuthService):
        data = LogInRequest(
            email="invalid@email.com",
            password=VALID_PASSWORD,
        )

        with pytest.raises(ValueError, match="Invalid email or password"):
            test_auth_service.log_in(data)

    def test_log_in_personnel_invalid_password(
        self, test_auth_service: AuthService, test_personnel: PersonalModel
    ):
        data = LogInRequest(
            email=test_personnel.email,
            password="invalid_password",
        )

        with pytest.raises(ValueError, match="Invalid email or password"):
            test_auth_service.log_in(data)
