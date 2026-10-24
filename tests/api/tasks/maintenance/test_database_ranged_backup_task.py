from datetime import timedelta

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupStatus, BackupTriggerMethod, BackupType, TaskStatus
from src.models import BackupModel, TaskModel
from src.schemas import BackupSchema
from src.tasks import database_ranged_backup
from src.utils import utcnow
from src.workflows import RangedBackupWorkflow


@pytest.mark.usefixtures("mock_task_db")
class TestDatabaseRangedBackupTask:
    def test_success_for_day(
        self,
        celery_worker: None,
        test_backup_session: Session,
        test_task_1: TaskModel,
    ):
        date_now = utcnow()
        task: AsyncResult = database_ranged_backup.apply_async(
            kwargs={
                "trigger": BackupTriggerMethod.MANUAL.value,
                "start_date": date_now.strftime("%Y-%m-%d"),
                "end_date": date_now.strftime("%Y-%m-%d"),
            },
            task_id=str(test_task_1.task_id),
        )
        backup = BackupSchema.model_validate(task.result)

        try:
            assert backup.status == BackupStatus.SUCCESS
            assert backup.backup_type == BackupType.RANGED_DAY
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

    def test_success_for_week(
        self,
        celery_worker: None,
        test_backup_session: Session,
        test_task_1: TaskModel,
    ):
        date_now = utcnow()
        start = date_now - timedelta(days=6)
        end = date_now

        task: AsyncResult = database_ranged_backup.apply_async(
            kwargs={
                "trigger": BackupTriggerMethod.MANUAL.value,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
            },
            task_id=str(test_task_1.task_id),
        )
        backup = BackupSchema.model_validate(task.result)

        try:
            assert backup.status == BackupStatus.SUCCESS
            assert backup.backup_type == BackupType.RANGED_WEEK
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

    def test_date_range_failure(
        self,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_task_1: TaskModel,
    ):
        date_now = utcnow()
        inv_date_range = date_now - timedelta(days=2)
        mocker.patch.object(
            RangedBackupWorkflow,
            "create_ranged_backup",
            side_effect=RuntimeError,
        )

        task: AsyncResult = database_ranged_backup.apply_async(
            kwargs={
                "trigger": BackupTriggerMethod.MANUAL.value,
                "start_date": inv_date_range.strftime("%Y-%m-%d"),
                "end_date": date_now.strftime("%Y-%m-%d"),
            },
            task_id=str(test_task_1.task_id),
        )
        backup = BackupSchema.model_validate(task.result)
        try:
            assert backup.status == BackupStatus.FAILURE
            assert backup.trigger_method == BackupTriggerMethod.MANUAL
            assert backup.error_message == "Variable date range provided was not a week"
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
        test_backup_session: Session,
        test_task_1: TaskModel,
    ):
        date_now = utcnow()
        mocker.patch.object(
            RangedBackupWorkflow,
            "create_ranged_backup",
            side_effect=RuntimeError,
        )

        task: AsyncResult = database_ranged_backup.apply_async(
            kwargs={
                "trigger": BackupTriggerMethod.MANUAL.value,
                "start_date": date_now.strftime("%Y-%m-%d"),
                "end_date": date_now.strftime("%Y-%m-%d"),
            },
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

    def test_task_cancelled(
        self,
        celery_worker: None,
        test_session: Session,
        test_task_1: TaskModel,
        test_backup_session: Session,
    ):
        test_task_1.status = TaskStatus.CANCELLED
        test_session.commit()

        date_now = utcnow()

        task: AsyncResult = database_ranged_backup.apply_async(
            kwargs={
                "trigger": BackupTriggerMethod.MANUAL.value,
                "start_date": date_now.strftime("%Y-%m-%d"),
                "end_date": date_now.strftime("%Y-%m-%d"),
            },
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
