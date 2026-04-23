import pytest

from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import PersonalModel, RankerModel
from src.schemas import (
    CreatePersonnelRequest,
    UpdatePersonnelRequest,
    InvalidSchema,
)
from src.services import AuthService


class TestAuthService:
    def test_register_personnel_success(
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
