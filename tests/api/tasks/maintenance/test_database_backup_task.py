import pytest
import re
import subprocess

from celery.result import AsyncResult
from pytest_mock import MockerFixture

from src.schemas import BackupSchema
from src.tasks import database_backup


class TestDatabaseBackupTask:
    def test_backup_success(self, mocker: MockerFixture, celery_worker: None):
        mocker.patch.object(subprocess, "run", return_value=None)
        task: AsyncResult = database_backup.delay()
        assert BackupSchema.model_validate(task.result)

    def test_backup_command_failure(self, mocker: MockerFixture, celery_worker: None):
        mock_error = subprocess.CalledProcessError(
            returncode=1, cmd="command", output="", stderr="error"
        )

        mocker.patch.object(subprocess, "run", side_effect=mock_error)

        with pytest.raises(SystemError, match="Unable to create database backup"):
            database_backup.delay()
