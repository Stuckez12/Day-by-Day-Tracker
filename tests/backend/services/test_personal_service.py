from backend.schemas import CreatePersonnelRequest
from backend.services import PersonalService


class TestPersonalService:
    def test_create_user_success(self, test_personal_service: PersonalService):
        data = CreatePersonnelRequest(
            first_name="Test",
            last_name="User",
        )

        personnel = test_personal_service.create_personnel(data)

        assert personnel.first_name == "Test"
        assert personnel.last_name == "User"

    def test_create_user_invalid_data(self, test_personal_service: PersonalService):
        assert False

    def test_create_user_no_data(self, test_personal_service: PersonalService):
        assert False

    def test_create_user_invalid_pydantic_model(
        self, test_personal_service: PersonalService
    ):
        assert False
