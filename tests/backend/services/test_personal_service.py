import pytest

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from uuid import UUID

from backend.models import PersonalModel
from backend.schemas import (
    CreatePersonnelRequest,
    UpdatePersonnelRequest,
    InvalidSchema,
)
from backend.services import PersonalService


class TestPersonalService:
    def test_create_user_success(
        self, test_session: Session, test_personal_service: PersonalService
    ):
        data = CreatePersonnelRequest(
            first_name="Test",
            last_name="User",
        )

        personnel = test_personal_service.create_personnel(data)

        assert personnel.first_name == "Test"
        assert personnel.last_name == "User"

        test_session.delete(personnel)
        test_session.commit()

    def test_create_user_invalid_pydantic_model(
        self, test_personal_service: PersonalService
    ):
        with pytest.raises(
            TypeError, match="Invalid data format provided for personnel"
        ):
            test_personal_service.create_personnel(InvalidSchema())

    def test_update_user_all_details(
        self, test_personnel: PersonalModel, test_personal_service: PersonalService
    ):
        data = UpdatePersonnelRequest(
            first_name="Updated",
            last_name="Updated",
        )

        updated_personnel = test_personal_service.update_personnel(
            test_personnel.id, data
        )

        assert updated_personnel.first_name == "Updated"
        assert updated_personnel.last_name == "Updated"

    def test_update_user_first_name(
        self, test_personnel: PersonalModel, test_personal_service: PersonalService
    ):
        data = UpdatePersonnelRequest(
            first_name="Updated",
        )

        updated_personnel = test_personal_service.update_personnel(
            test_personnel.id, data
        )

        assert updated_personnel.first_name == "Updated"
        assert updated_personnel.last_name == test_personnel.last_name

    def test_update_user_last_name(
        self, test_personnel: PersonalModel, test_personal_service: PersonalService
    ):
        data = UpdatePersonnelRequest(
            last_name="Updated",
        )

        updated_personnel = test_personal_service.update_personnel(
            test_personnel.id, data
        )

        assert updated_personnel.first_name == test_personnel.first_name
        assert updated_personnel.last_name == "Updated"

    def test_update_user_no_personnel_found(
        self, test_personal_service: PersonalService
    ):
        data = UpdatePersonnelRequest(
            first_name="Updated",
            last_name="Updated",
        )

        invalid_personnel_id = UUID("12345678-1234-5678-1234-567812345678")

        with pytest.raises(
            NoResultFound, match=f"Personnel {invalid_personnel_id} not found"
        ):
            test_personal_service.update_personnel(invalid_personnel_id, data)

    def test_delete_user_success(
        self, test_personnel: PersonalModel, test_personal_service: PersonalService
    ):
        test_personal_service.delete_personnel(test_personnel.id)
        no_personnel = test_personal_service.get_by_id(test_personnel.id)

        assert no_personnel is None

    def test_delete_user_does_not_exist(self, test_personal_service: PersonalService):
        invalid_personnel_id = UUID("12345678-1234-5678-1234-567812345678")

        with pytest.raises(
            NoResultFound, match=f"Personnel {invalid_personnel_id} not found"
        ):
            test_personal_service.delete_personnel(invalid_personnel_id)
