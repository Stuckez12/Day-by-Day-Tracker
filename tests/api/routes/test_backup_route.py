import uuid

from fastapi import status
from fastapi.testclient import TestClient

from src.models import BackupModel
from src.schemas import BackupSchema


class TestGetBackupRoute:
    def test_success_w_id(
        self,
        test_client_user_session: TestClient,
        test_backup: BackupModel,
    ):
        result = test_client_user_session.get(
            "/backup", params={"backup_id": str(test_backup.id)}
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert BackupSchema.model_validate(data)
        assert BackupSchema.model_validate(data) == BackupSchema.model_validate(
            test_backup
        )

    def test_success_w_celery_id(
        self,
        test_client_user_session: TestClient,
        test_backup: BackupModel,
    ):
        result = test_client_user_session.get(
            "/backup", params={"celery_id": str(test_backup.celery_id)}
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert BackupSchema.model_validate(data)
        assert BackupSchema.model_validate(data) == BackupSchema.model_validate(
            test_backup
        )

    def test_fails_when_no_id_provided(self, test_client_user_session: TestClient):
        result = test_client_user_session.get("/backup")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "You must provide either a backup id or celery task id"

    def test_not_found(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(
            "/backup", params={"backup_id": str(uuid.uuid4())}
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Backup does not exist"

    def test_not_found_w_celery_id(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(
            "/backup", params={"celery_id": str(uuid.uuid4())}
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Backup does not exist"
