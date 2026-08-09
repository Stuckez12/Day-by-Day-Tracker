import pytest
from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import PersonnelModel
from src.schemas import (
    CreatePersonnelRequest,
    InvalidSchema,
    UpdatePersonnelDetailsRequest,
    UpdatePersonnelEmailRequest,
    UpdatePersonnelPasswordRequest,
)
from src.services import PersonnelService
from tests.api.constants import VALID_PASSWORD


class TestCreatePersonnelPersonnelService:
    def test_success(
        self, test_session: Session, test_personal_service: PersonnelService
    ):
        data = CreatePersonnelRequest(
            email="email@email.com",
            password="Password1.",
            first_name="Test",
            last_name="User",
        )

        personnel = test_personal_service.create_personnel(data)

        try:
            assert personnel.email == data.email
            assert personnel.password == data.password
            assert personnel.first_name == data.first_name
            assert personnel.last_name == data.last_name

        finally:
            test_session.delete(personnel)
            test_session.commit()

    def test_invalid_pydantic_model(self, test_personal_service: PersonnelService):
        with pytest.raises(
            TypeError, match="Invalid data format provided for personnel"
        ):
            test_personal_service.create_personnel(InvalidSchema())  # type: ignore


class TestUpdatePersonnelDetailsPersonnelService:
    def test_success(
        self, test_personnel: PersonnelModel, test_personal_service: PersonnelService
    ):
        data = UpdatePersonnelDetailsRequest(
            first_name="Updated",
            last_name="Updated",
        )

        updated_personnel = test_personal_service.update_personnel_details(
            test_personnel, data
        )

        assert updated_personnel.first_name == "Updated"
        assert updated_personnel.last_name == "Updated"

    def test_only_update_first_name(
        self, test_personnel: PersonnelModel, test_personal_service: PersonnelService
    ):
        data = UpdatePersonnelDetailsRequest(
            first_name="Updated",
        )

        updated_personnel = test_personal_service.update_personnel_details(
            test_personnel, data
        )

        assert updated_personnel.first_name == "Updated"
        assert updated_personnel.last_name == test_personnel.last_name

    def test_only_update_last_name(
        self, test_personnel: PersonnelModel, test_personal_service: PersonnelService
    ):
        data = UpdatePersonnelDetailsRequest(
            last_name="Updated",
        )

        updated_personnel = test_personal_service.update_personnel_details(
            test_personnel, data
        )

        assert updated_personnel.first_name == test_personnel.first_name
        assert updated_personnel.last_name == "Updated"


class TestUpdatePersonnelEmailPersonnelService:
    def test_success(
        self, test_personnel: PersonnelModel, test_personal_service: PersonnelService
    ):
        data = UpdatePersonnelEmailRequest(
            email="updated@email.com",
        )

        updated_email = test_personal_service.update_personnel_email(
            test_personnel, data
        )
        assert updated_email.email == data.email


class TestUpdatePersonnelPasswordPersonnelService:
    def test_success(
        self, test_personnel: PersonnelModel, test_personal_service: PersonnelService
    ):
        data = UpdatePersonnelPasswordRequest(
            current_password=VALID_PASSWORD,
            new_password="NewPassword123",
        )

        updated_password = test_personal_service.update_personnel_password(
            test_personnel, data
        )

        assert pwd_hash.verify(data.new_password, updated_password.password)
