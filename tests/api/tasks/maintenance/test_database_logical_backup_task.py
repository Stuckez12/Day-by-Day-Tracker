import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupStatus, BackupTriggerMethod
from src.enums.task_status import TaskStatus
from src.models import BackupModel, TaskModel
from src.schemas import BackupSchema
from src.tasks import database_logical_backup
from src.utils import utcnow
from src.workflows import LogicalBackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestDatabaseLogicalBackupTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_logical_backup_zip_stored: BackupModel,
        test_task_1: TaskModel,
        test_backup_session: Session,
    ):
        mocker.patch.object(
            LogicalBackupWorkflow,
            "_get_database_date_range",
            return_value=(utcnow(), utcnow()),
        )
        assert test_logical_backup_zip_stored.meta

        task: AsyncResult = database_logical_backup.apply_async(
            kwargs={"trigger": BackupTriggerMethod.MANUAL.value},
            task_id=str(test_task_1.task_id),
        )
        backup = BackupSchema.model_validate(task.result)

        try:
            assert backup.status == BackupStatus.SUCCESS
            assert backup.trigger_method == BackupTriggerMethod.MANUAL
            assert backup.duration is not None
            assert backup.duration > 0
            assert backup.error_message is None
            assert backup.error_traceback is None
            assert backup.meta is not None

        finally:
            record = test_backup_session.get(BackupModel, backup.id)

            if record is not None:
                test_backup_session.delete(record)
                test_backup_session.commit()

    def test_task_cancelled(
        self,
        celery_worker: None,
        test_session: Session,
        test_task_1: TaskModel,
        test_backup_session: Session,
    ):
        test_task_1.status = TaskStatus.CANCELLED
        test_session.commit()

        task: AsyncResult = database_logical_backup.apply_async(
            kwargs={"trigger": BackupTriggerMethod.MANUAL.value},
            task_id=str(test_task_1.task_id),
        )
        backup = BackupSchema.model_validate(task.result)

        try:
            assert backup.status == BackupStatus.FAILURE
            assert backup.trigger_method == BackupTriggerMethod.MANUAL
            assert backup.duration is not None
            assert backup.duration > 0
            assert backup.error_message is not None
            assert backup.error_traceback is not None
            assert backup.meta is None

        finally:
            record = test_backup_session.get(BackupModel, backup.id)

            if record is not None:
                test_backup_session.delete(record)
                test_backup_session.commit()

    def test_workflow_failure(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_task_1: TaskModel,
        test_backup_session: Session,
    ):
        mocker.patch.object(
            LogicalBackupWorkflow,
            "create_logical_database_backup",
            side_effect=RuntimeError,
        )

        task: AsyncResult = database_logical_backup.apply_async(
            kwargs={"trigger": BackupTriggerMethod.MANUAL.value},
            task_id=str(test_task_1.task_id),
        )
        backup = BackupSchema.model_validate(task.result)

        try:
            assert backup.status == BackupStatus.FAILURE
            assert backup.trigger_method == BackupTriggerMethod.MANUAL
            assert backup.duration is not None
            assert backup.duration > 0
            assert backup.error_message is not None
            assert backup.error_traceback is not None
            assert backup.meta is None

        finally:
            record = test_backup_session.get(BackupModel, backup.id)

            if record is not None:
                test_backup_session.delete(record)
                test_backup_session.commit()
