from datetime import date
from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Query, Request, status

import src.tasks.task_management  # noqa
from src.core.permission_validator import PermissionValidator
from src.enums import BackupTriggerMethod
from src.tasks import (
    database_logical_backup,
    database_ranged_backup,
    simulate_celery_task,
    verify_logical_backup,
    verify_ranged_backup,
)


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
def run_database_ranged_backup(
    start_date: date = Query(...), end_date: date = Query(...)
):
    task: AsyncResult = database_ranged_backup.delay(
        trigger=BackupTriggerMethod.MANUAL.value,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
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
