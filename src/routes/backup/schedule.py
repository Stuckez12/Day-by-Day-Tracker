from datetime import date, datetime
from uuid import UUID

from celery.exceptions import OperationalError
from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.core.permission_validator import PermissionValidator
from src.enums import BackupType, TaskScheduleStatus
from src.exc import (
    HTTP_EXC_BACKUP_SCHEDULE_ALREADY_EXISTS,
    HTTP_EXC_BACKUP_SCHEDULE_NOT_FOUND,
    HTTP_EXC_ERROR_CANCELLING_QUEUED_TASK,
)
from src.schemas import (
    CreateScheduledBackupSchema,
    ScheduledBackupFilters,
    ScheduledBackupSchema,
)
from src.services.dependencies import BackupSchedulerServiceDep


api = APIRouter(
    prefix="/schedule",
    tags=["Backup Schedules"],
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)


@api.post(
    "",
    response_model=ScheduledBackupSchema,
    status_code=status.HTTP_200_OK,
)
def create_backup_schedule(
    service: BackupSchedulerServiceDep, data: CreateScheduledBackupSchema
):
    try:
        return service.create_schedule(data)

    except IntegrityError:
        existing_schedule_query = service.get_schedules_query(
            ScheduledBackupFilters(
                scheduled_from=data.scheduled_for, scheduled_to=data.scheduled_for
            )
        )
        existing_schedule = existing_schedule_query.first()

        if existing_schedule is not None:
            raise HTTP_EXC_BACKUP_SCHEDULE_ALREADY_EXISTS

        raise


@api.get(
    "/search",
    response_model=Page[ScheduledBackupSchema],
    status_code=status.HTTP_200_OK,
)
def search_backup_schedules(
    service: BackupSchedulerServiceDep,
    params: Params = Depends(),
    backup_type: BackupType = Query(None),
    status: TaskScheduleStatus = Query(None),
    scheduled_from: date = Query(None),
    scheduled_to: date = Query(None),
    date_from: datetime = Query(None),
    date_to: datetime = Query(None),
    dispatched_from: datetime = Query(None),
    dispatched_to: datetime = Query(None),
):
    filters = ScheduledBackupFilters(
        backup_type=backup_type,
        status=status,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        date_from=date_from,
        date_to=date_to,
        dispatched_from=dispatched_from,
        dispatched_to=dispatched_to,
    )

    query = service.get_schedules_query(filters)

    return paginate(query, params)


@api.get(
    "/{schedule_id}",
    response_model=ScheduledBackupSchema,
    status_code=status.HTTP_200_OK,
)
def get_backup_schedule(service: BackupSchedulerServiceDep, schedule_id: UUID):
    try:
        return service.get_schedule(schedule_id)

    except NoResultFound:
        raise HTTP_EXC_BACKUP_SCHEDULE_NOT_FOUND


@api.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backup_schedule(service: BackupSchedulerServiceDep, schedule_id: UUID):
    try:
        schedule = service.get_schedule(schedule_id)
        service.delete_schedule(schedule)

    except NoResultFound:
        raise HTTP_EXC_BACKUP_SCHEDULE_NOT_FOUND

    except OperationalError:
        raise HTTP_EXC_ERROR_CANCELLING_QUEUED_TASK
