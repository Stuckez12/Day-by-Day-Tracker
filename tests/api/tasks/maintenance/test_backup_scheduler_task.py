from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from src.enums import TaskScheduleStatus
from src.models import BackupScheduleModel
from src.tasks import backup_scheduler
from src.utils import utcnow


@pytest.mark.usefixtures("mock_task_db")
class TestBackupSchedulerTask:
    def test_generates_schedules(
        self,
        celery_worker: None,
        test_backup_session: Session,
    ):
        today = utcnow().date()
        existing_ids = [
            schedule.id
            for schedule in test_backup_session.query(BackupScheduleModel).all()
        ]
        new_schedules = test_backup_session.query(BackupScheduleModel).filter(
            BackupScheduleModel.id.notin_(existing_ids)
        )

        try:
            backup_scheduler.apply_async()

            schedules = new_schedules.all()
            assert {schedule.scheduled_for for schedule in schedules} == {
                today + timedelta(days=offset) for offset in range(130)
            }
            assert all(
                schedule.status == TaskScheduleStatus.QUEUED
                and schedule.celery_id is not None
                and schedule.dispatch_error is None
                for schedule in schedules
            )

        finally:
            new_schedules.delete()
            test_backup_session.commit()
