from pathlib import Path
from zipfile import ZipFile

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.common import utcnow
from src.core.s3_storage import ObjectStorage
from src.enums import BackupType, ObjectType
from src.models import MetaModel
from src.schemas import Metadata, MetadataDateRange, MetadataTool
from src.workflows import BackupWorkflow


class TestUpdateMetadataBackupWorkflow:
    def test_success(
        self, test_backup_workflow: BackupWorkflow, test_metadata: MetaModel
    ):
        assert test_metadata.last_verified

        past_verified_time = test_metadata.last_verified
        test_backup_workflow.update_verification_metadata_record()
        assert test_metadata.verified is True
        assert past_verified_time.replace(tzinfo=None) < test_metadata.last_verified

    def test_no_metadata(self, test_backup_workflow: BackupWorkflow):
        with pytest.raises(
            ValueError, match="Backup record does not have any attached metadata"
        ):
            test_backup_workflow.update_verification_metadata_record()


class TestGenerateMetadataBackupWorkflow:
    def test_success(self, mocker: MockerFixture, test_backup_workflow: BackupWorkflow):
        test_backup_workflow.metadata_date_range = MetadataDateRange(
            start=utcnow(), end=utcnow()
        )
        test_backup_workflow.metadata_tool = MetadataTool(name="tool", version="1")

        mocker.patch.object(BackupWorkflow, "_create_metadata_file", return_value=None)

        test_backup_workflow.generate_metadata(BackupType.LOGICAL)
        assert isinstance(test_backup_workflow.metadata, Metadata)

    def test_no_metadata_tools(self, test_backup_workflow: BackupWorkflow):
        test_backup_workflow.metadata_date_range = MetadataDateRange(
            start=utcnow(), end=utcnow()
        )

        with pytest.raises(ValueError, match="Backup tool used not set"):
            test_backup_workflow.generate_metadata(BackupType.LOGICAL)

    def test_no_metadata_date_range(self, test_backup_workflow: BackupWorkflow):
        test_backup_workflow.metadata_tool = MetadataTool(name="tool", version="1")

        with pytest.raises(ValueError, match="Backup date range not set"):
            test_backup_workflow.generate_metadata(BackupType.LOGICAL)


class TestRetrieveMetadataFileBackupWorkflow:
    def test_success(
        self, test_backup_workflow: BackupWorkflow, test_metadata_schema: Metadata
    ):
        test_backup_workflow.extracted_zip = True

        metadata_file_path = test_backup_workflow.temp_backup_path / "metadata.json"

        with metadata_file_path.open("w"):
            metadata_file_path.write_text(test_metadata_schema.model_dump_json())

        test_backup_workflow.retrieve_metadata_from_file()

        assert test_backup_workflow.metadata_file_path == metadata_file_path
        assert isinstance(test_backup_workflow.metadata, Metadata)
        assert test_backup_workflow.backup_file_path
        assert (
            test_backup_workflow.backup_file_path.name
            == test_metadata_schema.files[0].name
        )

    def test_zip_not_extracted(self, test_backup_workflow: BackupWorkflow):
        with pytest.raises(ValueError, match="ZIP file not extracted"):
            test_backup_workflow.retrieve_metadata_from_file()


class TestValidateChecksumsBackupWorkflow:
    def test_success(
        self,
        mocker: MockerFixture,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        mocker.patch.object(
            BackupWorkflow,
            "_generate_checksum",
            return_value=(None, test_metadata_schema.files[0].checksum.value),
        )
        test_backup_workflow.metadata = test_metadata_schema
        test_backup_workflow.validate_metadata_checksums()

        # No need for asserts as I am testing to ensure
        # that with the correct data it does not crash

    def test_checksum_mismatch(
        self,
        mocker: MockerFixture,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        mocker.patch.object(
            BackupWorkflow,
            "_generate_checksum",
            return_value=(None, "InvalidChecksum"),
        )
        test_backup_workflow.metadata = test_metadata_schema

        with pytest.raises(
            ValueError,
            match="Specified file 'backup.dump' corrupted. Checksum does not match",
        ):
            test_backup_workflow.validate_metadata_checksums()

    def test_no_metadata(self, test_backup_workflow: BackupWorkflow):
        with pytest.raises(ValueError, match="Metadata not set"):
            test_backup_workflow.validate_metadata_checksums()


class TestZipFilesBackupWorkflow:
    def test_success(
        self,
        test_file: Path,
        test_file_2: Path,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        test_backup_workflow.backup_file_path = test_file
        test_backup_workflow.metadata = test_metadata_schema
        test_backup_workflow.metadata_file_path = test_file_2

        expected_files = {test_file.name, test_file_2.name}

        test_backup_workflow.zip_all_backup_files()

        assert test_backup_workflow.zipped_backup_file_path is not None
        assert test_backup_workflow.zipped_backup_file_path.is_file()

        with ZipFile(test_backup_workflow.zipped_backup_file_path) as zf:
            assert set(zf.namelist()) == expected_files

    def test_no_backup_file_path(
        self,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        test_backup_workflow.metadata = test_metadata_schema
        test_backup_workflow.metadata_file_path = test_file

        with pytest.raises(ValueError, match="Backup file path not set"):
            test_backup_workflow.zip_all_backup_files()

    def test_no_metadata(
        self,
        test_file: Path,
        test_file_2: Path,
        test_backup_workflow: BackupWorkflow,
    ):
        test_backup_workflow.backup_file_path = test_file
        test_backup_workflow.metadata_file_path = test_file_2

        with pytest.raises(ValueError, match="Metadata not set"):
            test_backup_workflow.zip_all_backup_files()

    def test_no_metadata_file_path(
        self,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        test_backup_workflow.backup_file_path = test_file
        test_backup_workflow.metadata = test_metadata_schema

        with pytest.raises(ValueError, match="Metadata file path not set"):
            test_backup_workflow.zip_all_backup_files()


class TestUploadZipBackupWorkflow:
    def test_success(
        self,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_object_storage: ObjectStorage,
    ):
        test_backup_workflow.zipped_backup_file_path = test_file

        test_backup_workflow.upload_zip_to_object_storage()

        file_metadata = test_object_storage.file_metadata(
            ObjectType.BACKUP, test_file.name
        )
        assert file_metadata.directory.name == test_file.name

    def test_no_zip_file_path(self, test_backup_workflow: BackupWorkflow):
        with pytest.raises(ValueError, match="Zipped file path not set"):
            test_backup_workflow.upload_zip_to_object_storage()


class TestRetrieveZipBackupWorkflow:
    def test_success(
        self,
        mocker: MockerFixture,
        test_backup_session: Session,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_object_storage: ObjectStorage,
        test_metadata: MetaModel,
    ):
        mocker.patch.object(BackupWorkflow, "_extract_zip_file", return_value=None)

        with test_file.open("rb") as file:
            test_object_storage.upload_file(file, ObjectType.BACKUP, test_file.name)

        test_metadata.zip_path = test_file.name
        test_metadata.zip_filename = test_file.name
        test_backup_session.commit()

        test_backup_workflow.retrieve_zip_file()

        assert test_backup_workflow.zipped_backup_file_path
        assert test_backup_workflow.zipped_backup_file_path.is_file()

        test_backup_workflow.zipped_backup_file_path.unlink()
        test_object_storage.delete_file(ObjectType.BACKUP, test_file.name)

    def test_no_metadata(self, test_backup_workflow: BackupWorkflow):
        with pytest.raises(
            ValueError, match="Backup record does not have any attached metadata"
        ):
            test_backup_workflow.retrieve_zip_file()


class TestRetrieveDownloadedZipBackupWorkflow:
    def test_success(
        self,
        mocker: MockerFixture,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_object_storage: ObjectStorage,
    ):
        mocker.patch.object(BackupWorkflow, "_extract_zip_file", return_value=None)

        with test_file.open("rb") as file:
            test_object_storage.upload_file(file, ObjectType.BACKUP, test_file.name)

        test_backup_workflow.retrieve_downloaded_zip_file(test_file.name)

        assert test_backup_workflow.backup_uploaded is True
        assert test_backup_workflow.zipped_backup_file_path
        assert test_backup_workflow.zipped_backup_file_path.is_file()

        test_backup_workflow.zipped_backup_file_path.unlink()
        test_object_storage.delete_file(ObjectType.BACKUP, test_file.name)


class TestRecordBackupRowBackupWorkflow:
    def test_success(
        self,
        test_backup_session: Session,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_object_storage: ObjectStorage,
        test_metadata_schema: Metadata,
    ):
        with test_file.open("rb") as file:
            test_object_storage.upload_file(file, ObjectType.BACKUP, test_file.name)

        test_backup_workflow.metadata = test_metadata_schema
        test_backup_workflow.zipped_backup_file_path = test_file
        test_backup_workflow.backup_uploaded = True

        test_backup_workflow.record_backup_into_database()

        test_backup_session.refresh(test_backup_workflow.backup_record)

        assert test_backup_workflow.backup_record.meta is not None
        assert test_backup_workflow.backup_record.meta.zip_filename == test_file.name
        assert test_backup_workflow.backup_record.meta.zip_path == test_file.name

        test_object_storage.delete_file(ObjectType.BACKUP, test_file.name)

    def test_no_metadata(self, test_file: Path, test_backup_workflow: BackupWorkflow):
        test_backup_workflow.zipped_backup_file_path = test_file
        test_backup_workflow.backup_uploaded = True

        with pytest.raises(ValueError, match="Metadata not set"):
            test_backup_workflow.record_backup_into_database()

    def test_no_zip_file_path(
        self,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        test_backup_workflow.metadata = test_metadata_schema
        test_backup_workflow.backup_uploaded = True

        with pytest.raises(ValueError, match="Zipped file path not set"):
            test_backup_workflow.record_backup_into_database()

    def test_backup_not_uploaded(
        self,
        test_file: Path,
        test_backup_workflow: BackupWorkflow,
        test_metadata_schema: Metadata,
    ):
        test_backup_workflow.metadata = test_metadata_schema
        test_backup_workflow.zipped_backup_file_path = test_file

        with pytest.raises(
            ValueError,
            match="Backup must be uploaded into the object storage container",
        ):
            test_backup_workflow.record_backup_into_database()


class TestCleanupBackupWorkflow:
    def test_success(self, test_backup_workflow: BackupWorkflow):
        temp_file = test_backup_workflow.temp_backup_path / "test.txt"
        temp_file.write_bytes(b"hello world")

        test_backup_workflow.cleanup()

        assert not test_backup_workflow.temp_backup_path.exists()
