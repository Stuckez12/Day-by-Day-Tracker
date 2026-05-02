from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import PersonalModel
from src.schemas import SlimPersonnelSchema

from tests.api.constants import INVALID_PASSWORD, INVALID_PERSONNEL_ID, VALID_PASSWORD


class TestPersonalRoute:
    def test_get_personnel_success(
        self, test_client_v1: TestClient, test_personnel: PersonalModel
    ):
        result = test_client_v1.get(f"/personal?personnel_id={test_personnel.id}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_personnel.to_dict(clean=True)

    def test_get_personnel_invalid_id(self, test_client_v1: TestClient):
        result = test_client_v1.get(f"/personal?personnel_id={INVALID_PERSONNEL_ID}")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Personnel does not exist"

    def test_get_personnel_self_success(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.get(f"/personal/me")
        print(result.json())
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_personnel.to_dict(clean=True)

    def test_get_personnel_self_no_cookies(
        self,
        test_client_v1: TestClient,
    ):
        result = test_client_v1.get("/personal/me")
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        response = result.json()
        assert "detail" in response
        assert len(response["detail"]) == 1

        error_message = response["detail"][0]
        assert error_message["type"] == "missing"
        assert error_message["loc"] == ["cookie", "personnel_id"]
        assert error_message["msg"] == "Field required"
        assert error_message["input"] is None

    def test_get_all_personnel_success(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
        test_personnel_2: PersonalModel,
        test_personnel_3: PersonalModel,
    ):
        result = test_client_v1.get(f"/personal/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert len(data) == 3
        assert SlimPersonnelSchema.model_validate(data[0])
        assert SlimPersonnelSchema.model_validate(data[1])
        assert SlimPersonnelSchema.model_validate(data[2])

    def test_update_personnel_details_update_all_values(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/personal/me/details",
            json={
                "first_name": "Updated",
                "last_name": "Updated",
            },
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert data["id"] == str(test_personnel.id)
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Updated"

        personnel = (
            test_session.query(PersonalModel)
            .filter(PersonalModel.id == test_personnel.id)
            .one()
        )

        test_session.refresh(personnel)

        assert personnel == test_personnel
        assert personnel.first_name == "Updated"
        assert personnel.last_name == "Updated"

    def test_update_personnel_details_update_first_name(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/personal/me/details",
            json={
                "first_name": "Updated",
            },
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert data["id"] == str(test_personnel.id)
        assert data["first_name"] == "Updated"
        assert data["last_name"] == test_personnel.last_name

        personnel = (
            test_session.query(PersonalModel)
            .filter(PersonalModel.id == test_personnel.id)
            .one()
        )

        test_session.refresh(personnel)

        assert personnel == test_personnel
        assert personnel.first_name == "Updated"
        assert personnel.last_name == test_personnel.last_name

    def test_update_personnel_details_update_last_name(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/personal/me/details",
            json={
                "last_name": "Updated",
            },
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert data["id"] == str(test_personnel.id)
        assert data["first_name"] == test_personnel.first_name
        assert data["last_name"] == "Updated"

        personnel = (
            test_session.query(PersonalModel)
            .filter(PersonalModel.id == test_personnel.id)
            .one()
        )

        test_session.refresh(personnel)

        assert personnel == test_personnel
        assert personnel.first_name == test_personnel.first_name
        assert personnel.last_name == "Updated"

    def test_update_personnel_details_update_nothing(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/personal/me/details",
            json={},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert data["id"] == str(test_personnel.id)
        assert data["first_name"] == test_personnel.first_name
        assert data["last_name"] == test_personnel.last_name

        personnel = (
            test_session.query(PersonalModel)
            .filter(PersonalModel.id == test_personnel.id)
            .one()
        )

        test_session.refresh(personnel)

        assert personnel == test_personnel
        assert personnel.first_name == test_personnel.first_name
        assert personnel.last_name == test_personnel.last_name

    def test_update_personnel_details_does_not_exist(self, test_client_v1: TestClient):
        test_client_v1.cookies.set(name="personnel_id", value=INVALID_PERSONNEL_ID)

        result = test_client_v1.put("/personal/me/details", json={})
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == f"Personnel {INVALID_PERSONNEL_ID} not found"

    def test_update_personnel_details_invalid_empty_first_name(
        self, test_set_cookies: None, test_client_v1: TestClient
    ):
        result = test_client_v1.put(
            "/personal/me/details",
            json={"first_name": ""},
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()
        assert data["detail"][0]["msg"] == "Value error, first_name must not be empty"

    def test_update_personnel_details_invalid_empty_last_name(
        self, test_set_cookies: None, test_client_v1: TestClient
    ):
        result = test_client_v1.put(
            "/personal/me/details",
            json={"last_name": ""},
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()
        assert data["detail"][0]["msg"] == "Value error, last_name must not be empty"

    def test_update_personnel_email(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
    ):
        result = test_client_v1.put(
            "/personal/me/email",
            json={"email": "new@email.com"},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert data["email"] == "new@email.com"

    def test_update_personnel_password(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/personal/me/password",
            json={
                "current_password": VALID_PASSWORD,
                "new_password": "NewPassword123",
            },
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert data["id"] == str(test_personnel.id)
        assert data["first_name"] == test_personnel.first_name
        assert data["last_name"] == test_personnel.last_name
        assert data["email"] == test_personnel.email

    def test_update_personnel_password_incorrect_current_password(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
    ):
        result = test_client_v1.put(
            "/personal/me/password",
            json={
                "current_password": INVALID_PASSWORD,
                "new_password": "NewPassword123",
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert "detail" in data
        assert data["detail"] == "Current password incorrect"

    def test_update_personnel_password__password_hashing_fails(
        self,
        mocker: MockerFixture,
        test_set_cookies: None,
        test_client_v1: TestClient,
    ):
        mocker.patch.object(pwd_hash, "hash", side_effect=ValueError("Forced Error"))

        result = test_client_v1.put(
            "/personal/me/password",
            json={
                "current_password": VALID_PASSWORD,
                "new_password": "NewPassword123",
            },
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert "detail" in data
        assert data["detail"] == "Unable to hash password. Please try again"

    def test_delete_personnel_success(
        self,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.delete(f"/personal?id={test_personnel.id}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data is None

        personnel = (
            test_session.query(PersonalModel)
            .filter(PersonalModel.id == test_personnel.id)
            .scalar()
        )

        assert personnel is None

    def test_delete_personnel_does_not_exist(self, test_client_v1: TestClient):
        result = test_client_v1.delete(f"/personal?id={INVALID_PERSONNEL_ID}")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == f"Personnel {INVALID_PERSONNEL_ID} not found"
