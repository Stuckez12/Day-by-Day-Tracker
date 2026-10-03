from datetime import date
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Request, status

import src.tasks.task_management  # noqa
from src.common.dependencies import BackupDBSession, BackupServiceDep, DBSession
from src.core.permission_validator import PermissionValidator
from src.core.s3_storage.service import ObjectStorage
from src.enums import BackupTriggerMethod
from src.schemas.common import DateRangeRequest
from src.tasks import (
    database_logical_backup,
    database_ranged_backup,
    simulate_celery_task,
    verify_logical_backup,
    verify_ranged_backup,
)
from src.workflows.backup.ranged import RangedBackupWorkflow


api = APIRouter(prefix="/execute/task", tags=["Execute Task"])


@api.get("/simulate", status_code=status.HTTP_200_OK)
def run_task_simulation(_: Request):
    task: AsyncResult = simulate_celery_task.delay()

    return task.get()


@api.get(
    "/database-logical-backup",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)
def run_database_logical_backup(_: Request):
    task: AsyncResult = database_logical_backup.delay(
        trigger=BackupTriggerMethod.MANUAL.value
    )

    return task.get()


@api.get(
    "/database-ranged-backup",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)
def run_database_ranged_backup(_: Request):
    task: AsyncResult = database_ranged_backup.delay(
        trigger=BackupTriggerMethod.MANUAL.value,
        start_date="2026-09-13",
        end_date="2026-10-17",
    )

    return task.get()


@api.get(
    "/verify-logical-backup",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)
def run_verify_logical_backup(backup_id: UUID):
    task: AsyncResult = verify_logical_backup.delay(backup_id=backup_id)

    return task.get()


@api.get(
    "/verify-ranged-backup",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)
def run_verify_ranged_backup(backup_id: UUID):
    task: AsyncResult = verify_ranged_backup.delay(backup_id=backup_id)

    return task.get()


@api.get("/test", status_code=status.HTTP_200_OK)
def run_test(db: DBSession, bdb: BackupDBSession, service: BackupServiceDep):
    b = service.get_all()[0]
    w = RangedBackupWorkflow(
        db=db,
        backup_db=bdb,
        backup_record=b,
        object_storage=ObjectStorage(),
        date_range=DateRangeRequest(min_date=date(1, 1, 1), max_date=date(1, 1, 1)),
    )

    w.restore_backup_in_database(db, {})
