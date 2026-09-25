import uuid
from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.core.s3_storage import ObjectStorage
from src.enums import ObjectType
from src.exc import HTTP_EXC_NOT_AN_ADMIN
from src.models import BackupModel
from src.schemas import BackupSchema


class TestGetBackupRoute:
    def test_success_w_id(
        self,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
    ):
        result = test_client_admin_session.get(
            "/backup", params={"backup_id": str(test_backup.id)}
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert BackupSchema.model_validate(data)
        assert BackupSchema.model_validate(data) == BackupSchema.model_validate(
            test_backup
        )

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(
            "/backup", params={"backup_id": str(uuid.uuid4())}
        )
        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code

        data = result.json()
        assert "detail" in data
        assert data["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail

    def test_success_w_celery_id(
        self,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
    ):
        result = test_client_admin_session.get(
            "/backup", params={"celery_id": str(test_backup.celery_id)}
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert BackupSchema.model_validate(data)
        assert BackupSchema.model_validate(data) == BackupSchema.model_validate(
            test_backup
        )

    def test_fails_when_no_id_provided(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.get("/backup")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "You must provide either a backup id or celery task id"

    def test_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.get(
            "/backup", params={"backup_id": str(uuid.uuid4())}
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"

    def test_not_found_w_celery_id(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.get(
            "/backup", params={"celery_id": str(uuid.uuid4())}
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"


class TestGetAllBackupsRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
        test_backup_2: BackupModel,
    ):
        result = test_client_admin_session.get("/backup/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert len(data) == 2
        assert [BackupSchema.model_validate(backup) for backup in data]

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.get("/backup/all")
        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code

        data = result.json()
        assert "detail" in data
        assert data["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail


class TestUploadBackupRoute:
    def test_success(
        self,
        mocker: MockerFixture,
        test_backup_session: Session,
        test_client_admin_session: TestClient,
        test_backup_zip_name: Path,
        test_object_storage: ObjectStorage,
    ):
        task_id = str(uuid.uuid4())
        mocker.patch(
            "src.routes.backup.uploaded_backup_record_creation",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )

        with test_backup_zip_name.open("rb") as test_file_content:
            files = {"file": (test_backup_zip_name.name, test_file_content)}
            result = test_client_admin_session.post("/backup/upload", files=files)

        assert result.status_code == status.HTTP_202_ACCEPTED
        assert result.json() == {"task_id": task_id}

        file_metadata = test_object_storage.file_metadata(
            ObjectType.BACKUP, test_backup_zip_name.name
        )
        assert str(file_metadata.directory) == test_backup_zip_name.name
        assert file_metadata.bucket == ObjectType.BACKUP.value
        assert file_metadata.byte_size == 9696
        assert file_metadata.file_type == "application/zip"

        data = result.json()
        test_backup_session.execute(
            delete(BackupModel).where(BackupModel.celery_id == data["task_id"])
        )
        test_backup_session.commit()

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.post("/backup/upload")
        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code

        data = result.json()
        assert "detail" in data
        assert data["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail


class TestDownloadBackupRoute:
    def test_success(
        self, test_client_admin_session: TestClient, test_backup_zip_stored: BackupModel
    ):
        assert test_backup_zip_stored.meta

        result = test_client_admin_session.get(
            f"/backup/{test_backup_zip_stored.id}/download"
        )
        assert result.status_code == status.HTTP_200_OK
        assert (
            f'filename="{test_backup_zip_stored.meta.zip_filename}"'
            in result.headers["content-disposition"]
        )

        file_size = len(result.content)
        assert file_size == test_backup_zip_stored.meta.zip_size_bytes

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(f"/backup/{uuid.uuid4()}/download")
        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code

        data = result.json()
        assert "detail" in data
        assert data["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail

    def test_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.get(f"/backup/{uuid.uuid4()}/download")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"

    def test_no_metadata_present(
        self,
        test_backup_session: Session,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
    ):
        test_backup.meta = None
        test_backup_session.commit()

        result = test_client_admin_session.get(f"/backup/{test_backup.id}/download")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not have the required metadata"


class TestVerifyBackupRoute:
    def test_success(
        self,
        mocker: MockerFixture,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
    ):
        task_id = str(uuid.uuid4())

        mocker.patch(
            "src.routes.backup.verify_backup",
            **{"s.return_value.apply_async.return_value": mocker.Mock(id=task_id)},
        )

        result = test_client_admin_session.patch(f"/backup/{test_backup.id}/verify")
        assert result.status_code == status.HTTP_200_OK, result.json()
        assert result.json() == {"task_id": str(task_id)}

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.patch(f"/backup/{uuid.uuid4()}/verify")
        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code

        data = result.json()
        assert "detail" in data
        assert data["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail

    def test_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.patch(f"/backup/{uuid.uuid4()}/verify")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup does not exist"
