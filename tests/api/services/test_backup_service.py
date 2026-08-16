import uuid
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from pytest_mock import MockerFixture
from sqlalchemy.exc import NoResultFound

from src.models import BackupModel
from src.schemas.backup import Metadata
from src.services import BackupService


class TestGetBackupByIDService:
    def test_success(
        self, test_backup_service: BackupService, test_backup: BackupModel
    ):
        backup = test_backup_service.get_by_backup_id(test_backup.id)
        assert backup == test_backup

    def test_not_found(self, test_backup_service: BackupService):
        with pytest.raises(NoResultFound):
            test_backup_service.get_by_backup_id(uuid.uuid4())


class TestGetBackupByTaskIDService:
    def test_success(
        self, test_backup_service: BackupService, test_backup: BackupModel
    ):
        backup = test_backup_service.get_by_task_id(test_backup.celery_id)
        assert backup == test_backup

    def test_not_found(self, test_backup_service: BackupService):
        with pytest.raises(NoResultFound):
            test_backup_service.get_by_task_id(uuid.uuid4())


class TestGetAllBackupsService:
    def test_success(
        self,
        test_backup_service: BackupService,
        test_backup: BackupModel,
        test_backup_2: BackupModel,
    ):
        backups = test_backup_service.get_all()
        assert len(backups) == 2
        assert [type(backup) == BackupModel for backup in backups]


class TestSHA256BackupService:
    def test_success(
        self,
        test_backup_service: BackupService,
        test_file: Path,
    ):
        hash = test_backup_service.sha256_file(str(test_file))
        assert (
            hash == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )


class TestGenerateChecksumBackupService:
    def test_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        test_backup_service: BackupService,
        test_file: Path,
    ):
        mocker.patch("src.services.backup.app_config.BACKUP_PATH", str(tmp_path))
        Path(tmp_path / "temp").mkdir()
        file = test_backup_service.generate_checksum_file(str(test_file))

        with open(file, "rb") as f:
            assert sum(1 for _ in f) == 1, "The file provided is the incorrect size"

            f.seek(0)  # Point back to the beginning of the files
            assert (
                f.readline()
                == b"b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
            )


class TestCreateMetadataFileBackupService:
    def test_success(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
        test_backup_service: BackupService,
        test_metadata_schema: Metadata,
    ):
        mocker.patch("src.services.backup.app_config.BACKUP_PATH", str(tmp_path))
        Path(tmp_path / "temp").mkdir()
        file = test_backup_service.create_metadata_file(test_metadata_schema)

        with open(file, "rb") as f:
            assert sum(1 for _ in f) == 1, "The file provided is the incorrect size"

            f.seek(0)  # Point back to the beginning of the files
            assert f.readline().decode("utf-8") == test_metadata_schema.model_dump_json(
                exclude={"backup_id"}
            )


class TestUploadBackupService:
    async def test_success(
        self, tmp_path: Path, test_file: Path, test_backup_service: BackupService
    ):
        with open(test_file, "rb") as f:
            upload = UploadFile(
                file=BytesIO(test_file.read_bytes()), filename=test_file.name
            )

        file = await test_backup_service.upload_backup(upload)

        with open(tmp_path / file, "r") as f:
            assert sum(1 for _ in f) == 1, "The file provided is the incorrect size"

            f.seek(0)  # Point back to the beginning of the files
            assert f.readline() == "hello world"

    async def test_no_filename(
        self, test_file: Path, test_backup_service: BackupService
    ):
        with open(test_file, "rb") as f:
            upload = UploadFile(file=f)

        with pytest.raises(
            HTTPException,
            match="File uploaded does not have a file name attached. Cancelled file upload",
        ):
            await test_backup_service.upload_backup(upload)
