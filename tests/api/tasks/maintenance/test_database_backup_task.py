import subprocess

from celery.result import AsyncResult
from pytest_mock import MockerFixture

from src.enums import BackupTriggerMethod
from src.enums.backup.status import BackupStatus
from src.schemas import BackupSchema
from src.services import BackupService
from src.tasks import database_logical_backup


class TestDatabaseBackupTask:
    def test_backup_success(self, mocker: MockerFixture, celery_worker: None):
        mocker.patch.object(subprocess, "run", return_value=None)
        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        assert BackupSchema.model_validate(task.result)

    def test_backup_command_failure(self, mocker: MockerFixture, celery_worker: None):
        mocker.patch.object(
            BackupService, "create_logical_backup", side_effect=ValueError
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        assert BackupSchema.model_validate(task.result)

        schema = BackupSchema.model_validate(task.result)
        assert schema.status == BackupStatus.FAILURE
        assert schema.error_message is not None
        assert schema.error_traceback is not None
