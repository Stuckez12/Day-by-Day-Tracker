import subprocess
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.core.database import recreate_database
from src.models import RankerModel
from src.schemas import MetadataDateRange
from src.workflows import LogicalBackupWorkflow


class TestCreateLogicalDatabaseBackupWorkflow:
    def test_success(
        self,
        test_ranker: RankerModel,
        test_logical_backup_workflow: LogicalBackupWorkflow,
    ):
        test_logical_backup_workflow.create_logical_database_backup()

        assert test_logical_backup_workflow.backup_file_path
        assert test_logical_backup_workflow.backup_file_path.is_file()

        test_logical_backup_workflow.backup_file_path.unlink()
        assert not test_logical_backup_workflow.backup_file_path.exists()
        assert len(test_logical_backup_workflow.metadata_files) == 1

        assert test_logical_backup_workflow.metadata_tool
        assert test_logical_backup_workflow.metadata_tool.name == "pg_dump"
        assert test_logical_backup_workflow.metadata_tool.version in [
            "pg_dump (PostgreSQL) 17.11 (Debian 17.11-1.pgdg12+2)",
            "pg_dump (PostgreSQL) 17.11 (Ubuntu 17.11-1.pgdg24.04+2)",
        ]
        assert test_logical_backup_workflow.metadata_date_range == MetadataDateRange(
            start=test_ranker.created_at, end=test_ranker.updated_at
        )

    def test_subprocess_backing_up_fails(
        self, mocker: MockerFixture, test_logical_backup_workflow: LogicalBackupWorkflow
    ):
        mocker.patch.object(
            subprocess,
            "run",
            side_effect=subprocess.CalledProcessError(1, "command here"),
        )

        with pytest.raises(SystemError):
            test_logical_backup_workflow.create_logical_database_backup()


class TestVerifyBackupFileWorkflow:
    def test_success(
        self, mocker: MockerFixture, test_logical_backup_workflow: LogicalBackupWorkflow
    ):
        test_database_name = "restore_backup_testing_db"
        original_recreate_database = recreate_database

        mocker.patch.object(subprocess, "run", return_value=None)

        test_logical_backup_workflow.backup_file_path = Path()

        with mocker.patch(
            "src.workflows.backup.logical.recreate_database",
            side_effect=lambda _: original_recreate_database(test_database_name),
        ):
            test_logical_backup_workflow.verify_backup_file()

    def test_no_backup_file_path(
        self, test_logical_backup_workflow: LogicalBackupWorkflow
    ):
        with pytest.raises(ValueError, match="Backup file path not set"):
            test_logical_backup_workflow.verify_backup_file()

    def test_subprocess_verification_fails(
        self, mocker: MockerFixture, test_logical_backup_workflow: LogicalBackupWorkflow
    ):
        mocker.patch.object(
            subprocess,
            "run",
            side_effect=subprocess.CalledProcessError(1, "command here"),
        )

        test_logical_backup_workflow.backup_file_path = Path()

        with pytest.raises(SystemError):
            test_logical_backup_workflow.verify_backup_file()


@pytest.mark.skip(reason="TODO when photos have been implemented")
class TestCreateObjectFolderBackupWorkflow:
    def test_success(self, test_logical_backup_workflow: LogicalBackupWorkflow):
        test_logical_backup_workflow.create_object_folder_backup()
