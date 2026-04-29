import pytest

from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session
from uuid import UUID

from src.common.password_hash import pwd_hash
from src.models import PersonalModel

from tests.api.constants import INVALID_PASSWORD, VALID_PASSWORD


class TestAuthRoute:
    def test_register_personnel_success(
        self, test_session: Session, test_client_v1: TestClient
    ):
        request_data = {
            "email": "email@email.com",
            "password": "Password1.",
            "first_name": "Test",
            "last_name": "User",
        }

        result = test_client_v1.post(
            "/auth/register",
            json=request_data,
        )
        assert result.status_code == status.HTTP_201_CREATED

        data = result.json()
        assert UUID(data["id"])
        assert data["first_name"] == request_data["first_name"]
        assert data["last_name"] == request_data["last_name"]

        test_session.query(PersonalModel).delete()
        test_session.commit()

    @pytest.mark.parametrize(
        ("empty_param_name", "expected_response"),
        [
            ("email", "Value error, email must not be empty"),
            ("password", "Value error, password must not be empty"),
            ("first_name", "Value error, first_name must not be empty"),
            ("last_name", "Value error, last_name must not be empty"),
        ],
    )
    def test_register_personnel_empty_data(
        self, test_client_v1: TestClient, empty_param_name: str, expected_response: str
    ):
        data = {
            "email": "dead@email.com",
            "password": "Password1.",
            "first_name": "Test",
            "last_name": "User",
        }
        data[empty_param_name] = ""

        result = test_client_v1.post(
            "/auth/register",
            json=data,
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()

        assert data["detail"][0]["msg"] == expected_response

    def test_register_personnel_email_already_in_use(
        self, test_client_v1: TestClient, test_personnel: PersonalModel
    ):
        result = test_client_v1.post(
            "/auth/register",
            json={
                "email": test_personnel.email,
                "password": "Password1.",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Email already in use"

    def test_register_personnel_password_hashing_fails(
        self,
        mocker: MockerFixture,
        test_client_v1: TestClient,
    ):
        mocker.patch.object(pwd_hash, "hash", side_effect=ValueError("Forced Error"))

        result = test_client_v1.post(
            "/auth/register",
            json={
                "email": "email@email.com",
                "password": "Password1.",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Unable to hash password. Please try again"

    def test_log_in(self, test_client_v1: TestClient, test_personnel: PersonalModel):
        result = test_client_v1.post(
            "/auth/login",
            json={
                "email": test_personnel.email,
                "password": VALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.cookies["personnel_id"]

    def test_log_in_user_does_not_exist(self, test_client_v1: TestClient):
        result = test_client_v1.post(
            "/auth/login",
            json={
                "email": "invalid@email.com",
                "password": VALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Invalid email or password"

    def test_log_in_invalid_password(
        self, test_client_v1: TestClient, test_personnel: PersonalModel
    ):
        result = test_client_v1.post(
            "/auth/login",
            json={
                "email": test_personnel.email,
                "password": INVALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Invalid email or password"

    def test_log_out(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.post(
            "/auth/logout",
            json={
                "email": test_personnel.email,
                "password": INVALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert test_client_v1.cookies.get("personnel_id") is None
