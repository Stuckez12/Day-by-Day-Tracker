import uuid

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.exc import HTTP_EXC_NOT_AN_ADMIN
from src.models import BackupScheduleModel


class TestDeleteBackupScheduleRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        result = test_client_admin_session.delete(
            f"/backup/schedule/{test_logical_backup_schedule.id}"
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.delete(f"/backup/schedule/{uuid.uuid4()}")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup schedule does not exist"

    def test_already_deleted(
        self,
        test_backup_session: Session,
        test_client_admin_session: TestClient,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        test_backup_session.delete(test_logical_backup_schedule)
        test_backup_session.commit()

        result = test_client_admin_session.delete(
            f"/backup/schedule/{test_logical_backup_schedule.id}"
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup schedule does not exist"

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.delete(f"/backup/schedule/{uuid.uuid4()}")

        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code
        assert result.json()["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail

    def test_invalid_schedule_id(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.delete("/backup/schedule/invalid-uuid")
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
