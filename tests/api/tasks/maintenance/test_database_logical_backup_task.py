import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture

from src.common import utcnow
from src.enums import BackupStatus, BackupTriggerMethod
from src.models import BackupModel
from src.schemas import BackupSchema
from src.tasks import database_logical_backup
from src.workflows import BackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestDatabaseLogicalBackupTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_zip_stored: BackupModel,
    ):
        mocker.patch.object(
            BackupWorkflow,
            "_get_database_date_range",
            return_value=(utcnow(), utcnow()),
        )
        assert test_backup_zip_stored.meta

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.SUCCESS
        assert backup.trigger_method == BackupTriggerMethod.MANUAL
        assert backup.duration is not None
        assert backup.duration > 0
        assert backup.error_message is None
        assert backup.error_traceback is None
        assert backup.meta is not None

    def test_workflow_failure(self, mocker: MockerFixture, celery_worker: None):
        mocker.patch.object(
            BackupWorkflow, "create_logical_database_backup", side_effect=RuntimeError
        )

        task: AsyncResult = database_logical_backup.delay(
            trigger=BackupTriggerMethod.MANUAL.value
        )
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.FAILURE
        assert backup.trigger_method == BackupTriggerMethod.MANUAL
        assert backup.duration is not None
        assert backup.duration > 0
        assert backup.error_message is not None
        assert backup.error_traceback is not None
        assert backup.meta is None
