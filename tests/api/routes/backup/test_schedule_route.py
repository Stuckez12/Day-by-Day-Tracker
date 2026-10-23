import uuid
from datetime import datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.enums import BackupType, TaskScheduleStatus
from src.exc import HTTP_EXC_NOT_AN_ADMIN
from src.models import BackupScheduleModel
from src.schemas import CreateScheduledBackupSchema, ScheduledBackupSchema


class TestDeleteBackupScheduleRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        result = test_client_admin_session.delete(
            f"/backup/schedule/{test_logical_backup_schedule.id}"
        )
        assert result.status_code == status.HTTP_204_NO_CONTENT

    def test_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.delete(f"/backup/schedule/{uuid.uuid4()}")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup schedule does not exist"

    def test_already_deleted(
        self,
        test_backup_session: Session,
        test_client_admin_session: TestClient,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        test_backup_session.delete(test_logical_backup_schedule)
        test_backup_session.commit()

        result = test_client_admin_session.delete(
            f"/backup/schedule/{test_logical_backup_schedule.id}"
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup schedule does not exist"

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.delete(f"/backup/schedule/{uuid.uuid4()}")

        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code
        assert result.json()["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail

    def test_invalid_schedule_id(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.delete("/backup/schedule/invalid-uuid")
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestCreateBackupScheduleRoute:
    def test_logical_success(
        self,
        test_client_admin_session: TestClient,
        test_backup_session: Session,
    ):
        scheduled_for = datetime.now() + timedelta(days=200)
        payload = {
            "celery_id": str(uuid.uuid4()),
            "backup_type": BackupType.LOGICAL.value,
            "scheduled_for": scheduled_for.isoformat(),
        }

        try:
            result = test_client_admin_session.post("/backup/schedule", json=payload)
            assert result.status_code == status.HTTP_200_OK

            data = ScheduledBackupSchema.model_validate(result.json())
            schedule = test_backup_session.get(BackupScheduleModel, data.id)
            assert schedule is not None
            assert data == ScheduledBackupSchema.model_validate(schedule)
            assert data.celery_id == uuid.UUID(payload["celery_id"])
            assert data.backup_type == BackupType.LOGICAL
            assert data.scheduled_for.date() == scheduled_for.date()
            assert data.status == TaskScheduleStatus.QUEUED
            assert data.dispatch_error is None
            assert data.date_range_start is None
            assert data.date_range_end is None

        finally:
            test_backup_session.query(BackupScheduleModel).filter(
                BackupScheduleModel.celery_id == uuid.UUID(payload["celery_id"])
            ).delete()
            test_backup_session.commit()

    def test_ranged_day_success(
        self,
        test_client_admin_session: TestClient,
        test_backup_session: Session,
    ):
        scheduled_for = datetime.now() + timedelta(days=200)
        payload = {
            "celery_id": str(uuid.uuid4()),
            "backup_type": BackupType.RANGED_DAY.value,
            "scheduled_for": scheduled_for.isoformat(),
            "date_range_start": (scheduled_for - timedelta(days=0)).isoformat(),
            "date_range_end": scheduled_for.isoformat(),
        }

        try:
            result = test_client_admin_session.post("/backup/schedule", json=payload)
            assert result.status_code == status.HTTP_200_OK

            data = ScheduledBackupSchema.model_validate(result.json())
            schedule = test_backup_session.get(BackupScheduleModel, data.id)
            assert schedule is not None
            assert data == ScheduledBackupSchema.model_validate(schedule)
            assert data.celery_id == uuid.UUID(payload["celery_id"])
            assert data.backup_type == BackupType.RANGED_DAY
            assert data.scheduled_for.date() == scheduled_for.date()
            assert data.status == TaskScheduleStatus.QUEUED
            assert data.dispatch_error is None
            assert data.date_range_start == scheduled_for
            assert data.date_range_end == scheduled_for

        finally:
            test_backup_session.query(BackupScheduleModel).filter(
                BackupScheduleModel.celery_id == uuid.UUID(payload["celery_id"])
            ).delete()
            test_backup_session.commit()

    def test_ranged_week_success(
        self,
        test_client_admin_session: TestClient,
        test_backup_session: Session,
    ):
        scheduled_for = datetime.now() + timedelta(days=200)
        payload = {
            "celery_id": str(uuid.uuid4()),
            "backup_type": BackupType.RANGED_WEEK.value,
            "scheduled_for": scheduled_for.isoformat(),
            "date_range_start": (scheduled_for - timedelta(days=6)).isoformat(),
            "date_range_end": scheduled_for.isoformat(),
        }

        try:
            result = test_client_admin_session.post("/backup/schedule", json=payload)
            assert result.status_code == status.HTTP_200_OK

            data = ScheduledBackupSchema.model_validate(result.json())
            schedule = test_backup_session.get(BackupScheduleModel, data.id)
            assert schedule is not None
            assert data == ScheduledBackupSchema.model_validate(schedule)
            assert data.celery_id == uuid.UUID(payload["celery_id"])
            assert data.backup_type == BackupType.RANGED_WEEK
            assert data.scheduled_for.date() == scheduled_for.date()
            assert data.status == TaskScheduleStatus.QUEUED
            assert data.dispatch_error is None
            assert data.date_range_start == scheduled_for - timedelta(days=6)
            assert data.date_range_end == scheduled_for

        finally:
            test_backup_session.query(BackupScheduleModel).filter(
                BackupScheduleModel.celery_id == uuid.UUID(payload["celery_id"])
            ).delete()
            test_backup_session.commit()

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.post(
            "/backup/schedule",
            json={
                "celery_id": str(uuid.uuid4()),
                "backup_type": BackupType.LOGICAL.value,
                "scheduled_for": datetime.now().isoformat(),
            },
        )
        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code
        assert result.json()["detail"] == HTTP_EXC_NOT_AN_ADMIN.detail

    def test_invalid_backup_range(self, test_client_admin_session: TestClient):
        scheduled_for = datetime.now()
        result = test_client_admin_session.post(
            "/backup/schedule",
            json={
                "celery_id": str(uuid.uuid4()),
                "backup_type": BackupType.RANGED_DAY.value,
                "scheduled_for": scheduled_for.isoformat(),
                "date_range_start": scheduled_for.isoformat(),
                "date_range_end": (scheduled_for + timedelta(days=1)).isoformat(),
            },
        )
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        data = result.json()
        assert data["detail"][0]["loc"] == ["body"]
        assert (
            "Daily backups must cover a single calendar day" in data["detail"][0]["msg"]
        )


class TestGetBackupScheduleRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        result = test_client_admin_session.get(
            f"/backup/schedule/{test_logical_backup_schedule.id}"
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert ScheduledBackupSchema.model_validate(data) == (
            ScheduledBackupSchema.model_validate(test_logical_backup_schedule)
        )

    def test_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.get(f"/backup/schedule/{uuid.uuid4()}")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Backup schedule does not exist"


class TestSearchBackupSchedulesRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        result = test_client_admin_session.get("/backup/schedule/search")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 1
        assert ScheduledBackupSchema.model_validate(
            data["items"][0]
        ) == ScheduledBackupSchema.model_validate(test_logical_backup_schedule)

    def test_pagination(
        self,
        test_client_admin_session: TestClient,
        test_backup_session: Session,
        test_logical_backup_schedule: BackupScheduleModel,
    ):
        later_schedule = BackupScheduleModel(
            CreateScheduledBackupSchema(
                celery_id=uuid.uuid4(),
                backup_type=BackupType.LOGICAL,
                scheduled_for=datetime.now() + timedelta(days=1),
            )
        )
        test_backup_session.add(later_schedule)
        test_backup_session.commit()

        try:
            for page, schedule in enumerate(
                [later_schedule, test_logical_backup_schedule], start=1
            ):
                result = test_client_admin_session.get(
                    "/backup/schedule/search", params={"page": page, "size": 1}
                )
                assert result.status_code == status.HTTP_200_OK

                data = result.json()
                assert data["total"] == 2
                assert data["pages"] == 2
                assert data["page"] == page
                assert data["size"] == 1
                assert [item["id"] for item in data["items"]] == [str(schedule.id)]

        finally:
            test_backup_session.delete(later_schedule)
            test_backup_session.commit()

    def test_combined_filters(
        self,
        test_client_admin_session: TestClient,
        test_backup_session: Session,
        test_ranged_day_backup_schedule: BackupScheduleModel,
    ):
        schedule = test_ranged_day_backup_schedule
        other_schedule = BackupScheduleModel(
            CreateScheduledBackupSchema(
                celery_id=uuid.uuid4(),
                backup_type=BackupType.LOGICAL,
                scheduled_for=datetime.now() + timedelta(days=1),
            )
        )
        test_backup_session.add(other_schedule)
        test_backup_session.commit()

        assert schedule.date_range_start
        assert schedule.date_range_end

        params = {
            "backup_type": BackupType.RANGED_DAY.value,
            "status": TaskScheduleStatus.QUEUED.value,
            "scheduled_from": schedule.scheduled_for.isoformat(),
            "scheduled_to": schedule.scheduled_for.isoformat(),
            "date_from": schedule.date_range_start.isoformat(),
            "date_to": schedule.date_range_end.isoformat(),
            "dispatched_from": schedule.dispatched_at.isoformat(),
            "dispatched_to": schedule.dispatched_at.isoformat(),
        }

        try:
            result = test_client_admin_session.get(
                "/backup/schedule/search", params=params
            )
            assert result.status_code == status.HTTP_200_OK
            assert result.json()["total"] == 1
            assert [item["id"] for item in result.json()["items"]] == [str(schedule.id)]

            params["status"] = TaskScheduleStatus.RUNNING.value
            result = test_client_admin_session.get(
                "/backup/schedule/search", params=params
            )
            assert result.status_code == status.HTTP_200_OK

            data = result.json()
            assert data["total"] == 0
            assert data["items"] == []

        finally:
            test_backup_session.delete(other_schedule)
            test_backup_session.commit()
