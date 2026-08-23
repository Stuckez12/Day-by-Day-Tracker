import uuid
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

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
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"

    def test_not_found_w_celery_id(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(
            "/backup", params={"celery_id": str(uuid.uuid4())}
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"


class TestGetAllBackupsRoute:
    def test_success(
        self,
        test_client_user_session: TestClient,
        test_backup: BackupModel,
        test_backup_2: BackupModel,
    ):
        result = test_client_user_session.get("/backup/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert len(data) == 2
        assert [BackupSchema.model_validate(backup) for backup in data]


class TestUploadBackupRoute:
    def test_success(
        self,
        mocker: MockerFixture,
        test_file: Path,
        test_temp_backup_path: Path,
        test_client_user_session: TestClient,
    ):
        task_id = str(uuid.uuid4())
        mocker.patch(
            "src.tasks.uploaded_backup_record_creation",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )

        with test_file.open("rb") as test_file_content:
            files = {"file": (test_file.name, test_file_content)}
            result = test_client_user_session.post("/backup/upload", files=files)

        assert result.status_code == status.HTTP_202_ACCEPTED
        assert result.json() == {"task_id": str(task_id)}

        test_uploaded_file = test_temp_backup_path / test_file.name
        assert test_uploaded_file.exists()
        assert test_uploaded_file.read_bytes() == test_file.read_bytes()


class TestDownloadBackupRoute:
    def test_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        test_client_user_session: TestClient,
        test_backup_w_file: Path,
        test_backup: BackupModel,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(tmp_path))

        result = test_client_user_session.get(f"/backup/{test_backup.id}/download")
        assert result.status_code == status.HTTP_200_OK

        file = result.read()
        assert file == test_backup_w_file.read_bytes()

    def test_not_found(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(f"/backup/{uuid.uuid4()}/download")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"

    def test_no_metadata_present(
        self,
        test_backup_session: Session,
        test_client_user_session: TestClient,
        test_backup: BackupModel,
    ):
        test_backup.meta = None
        test_backup_session.commit()

        result = test_client_user_session.get(f"/backup/{test_backup.id}/download")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not have the required metadata"


class TestVerifyBackupRoute:
    def test_success(
        self,
        mocker: MockerFixture,
        test_client_user_session: TestClient,
        test_backup_w_file: Path,
        test_backup: BackupModel,
    ):
        mocker.patch("src.routes.backup.verify_backup.s", uuid.uuid4())

        result = test_client_user_session.get(f"/backup/{test_backup.id}/download")
        assert result.status_code == status.HTTP_200_OK

        file = result.read()
        assert file == test_backup_w_file.read_bytes()

    def test_not_found(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(f"/backup/{uuid.uuid4()}/download")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"
