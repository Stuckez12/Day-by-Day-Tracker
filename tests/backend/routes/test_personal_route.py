from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID

from backend.models import PersonalModel

from tests.backend.constants import INVALID_PERSONNEL_ID


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
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_personnel.to_dict(clean=True)

    def test_get_personnel_self_no_cookies(
        self,
        test_client_v1: TestClient,
    ):
        result = test_client_v1.get(f"/personal/me", cookies=None)
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Personnel does not exist"

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

        personnel_1, personnel_2, personnel_3 = data[:3]
        assert personnel_1 == test_personnel.to_dict(clean=True)
        assert personnel_2 == test_personnel_2.to_dict(clean=True)
        assert personnel_3 == test_personnel_3.to_dict(clean=True)

    def test_create_personnel_success(
        self,
        test_session: Session,
        test_client_v1: TestClient,
    ):
        result = test_client_v1.post(
            f"/personal",
            json={
                "first_name": "Create",
                "last_name": "User",
            },
        )
        assert result.status_code == status.HTTP_201_CREATED

        data = result.json()
        assert UUID(data["id"])
        assert datetime.fromisoformat(data["created_at"])
        assert datetime.fromisoformat(data["updated_at"])
        assert data["first_name"] == "Create"
        assert data["last_name"] == "User"

        model = (
            test_session.query(PersonalModel)
            .filter(PersonalModel.id == data["id"])
            .one()
        )
        test_session.delete(model)
        test_session.commit()

    def test_create_personnel_empty_data(self, test_client_v1: TestClient):
        result = test_client_v1.post(
            f"/personal",
            json={
                "first_name": "",
                "last_name": "",
            },
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()
        assert data["detail"][0]["msg"] == "Value error, first_name must not be empty"
        assert data["detail"][1]["msg"] == "Value error, last_name must not be empty"

    def test_update_personnel_update_all_values(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/personal",
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

    def test_update_personnel_update_first_name(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            f"/personal",
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

    def test_update_personnel_update_last_name(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            f"/personal",
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

    def test_update_personnel_update_nothing(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            f"/personal",
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

    def test_update_personnel_does_not_exist(self, test_client_v1: TestClient):
        test_client_v1.cookies.set(name="personnel_id", value=INVALID_PERSONNEL_ID)

        result = test_client_v1.put("/personal", json={})
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == f"Personnel {INVALID_PERSONNEL_ID} not found"

    def test_update_personnel_invalid_empty_first_name(
        self, test_set_cookies: None, test_client_v1: TestClient
    ):
        result = test_client_v1.put(
            f"/personal",
            json={"first_name": ""},
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()
        assert data["detail"][0]["msg"] == "Value error, first_name must not be empty"

    def test_update_personnel_invalid_empty_last_name(
        self, test_set_cookies: None, test_client_v1: TestClient
    ):
        result = test_client_v1.put(
            f"/personal",
            json={"last_name": ""},
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()
        assert data["detail"][0]["msg"] == "Value error, last_name must not be empty"

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

    def test_select_personnel_success(
        self,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            f"/personal/select",
            json={"id": str(test_personnel.id)},
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT
        assert result.cookies.get("personnel_id") == str(test_personnel.id)

    def test_select_personnel_does_not_exist(self, test_client_v1: TestClient):
        result = test_client_v1.put(
            f"/personal/select",
            json={"id": INVALID_PERSONNEL_ID},
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == f"Personnel {INVALID_PERSONNEL_ID} not found"
