from uuid import UUID

import jwt
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session
from tests.api.constants import INVALID_PASSWORD, VALID_PASSWORD

from src.core.password_hash import pwd_hash
from src.models import PersonnelModel
from src.schemas.personnel import SlimPersonnelSchema
from src.settings import app_config


class TestRegistrationRoute:
    def test_success(self, test_session: Session, test_app: TestClient):
        request_data = {
            "email": "test@email.now",
            "password": "Password1.",
            "first_name": "Test",
            "last_name": "User",
        }

        result = test_app.post(
            "/auth/register",
            json=request_data,
        )
        assert result.status_code == status.HTTP_201_CREATED

        data = result.json()
        assert UUID(data["id"])
        assert data["first_name"] == request_data["first_name"]
        assert data["last_name"] == request_data["last_name"]

        test_session.query(PersonnelModel).delete()
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
    def test_empty_data(
        self,
        test_app: TestClient,
        empty_param_name: str,
        expected_response: str,
    ):
        data = {
            "email": "dead@email.com",
            "password": "Password1.",
            "first_name": "Test",
            "last_name": "User",
        }
        data[empty_param_name] = ""

        result = test_app.post(
            "/auth/register",
            json=data,
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()

        assert data["detail"][0]["msg"] == expected_response

    def test_email_already_in_use(
        self,
        test_client_user_session: TestClient,
        test_session_personnel: PersonnelModel,
    ):
        result = test_client_user_session.post(
            "/auth/register",
            json={
                "email": test_session_personnel.email,
                "password": "Password1.",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Email already in use"

    def test_password_hashing_fails(
        self,
        mocker: MockerFixture,
        test_client_user_session: TestClient,
    ):
        mocker.patch.object(pwd_hash, "hash", side_effect=ValueError("Forced Error"))

        result = test_client_user_session.post(
            "/auth/register",
            json={
                "email": "test@email.now",
                "password": "Password1.",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Unable to hash password. Please try again"


class TestLogInRoute:
    def test_success(
        self,
        test_app: TestClient,
        test_session_personnel: PersonnelModel,
    ):
        result = test_app.post(
            "/auth/login",
            json={
                "email": test_session_personnel.email,
                "password": VALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert jwt.decode(
            data.get("access_token"), app_config.JWT_SECRET, algorithms=["HS256"]
        )
        assert data.get("token_type") == "bearer"
        assert SlimPersonnelSchema.model_validate(data.get("personnel")), (
            "Invalid schema returned"
        )
        assert SlimPersonnelSchema.model_validate(
            data.get("personnel")
        ) == SlimPersonnelSchema.model_validate(test_session_personnel), (
            "Mismatched schema returned"
        )

    def test_invalid_email(self, test_app: TestClient, test_personnel: PersonnelModel):
        result = test_app.post(
            "/auth/login",
            json={
                "email": "invalid@email.com",
                "password": VALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Invalid email or password"

    def test_invalid_password(
        self, test_app: TestClient, test_personnel: PersonnelModel
    ):
        result = test_app.post(
            "/auth/login",
            json={
                "email": test_personnel.email,
                "password": INVALID_PASSWORD,
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Invalid email or password"
