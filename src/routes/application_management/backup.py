from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import NoResultFound

from src.core.permission_validator import PermissionValidator
from src.exc import (
    HTTP_EXC_APP_SEETINGS_UNABLE_TO_FETCH_MODIFY_CONFIG,
    HTTP_EXC_BACKUP_NOT_FOUND,
)
from src.schemas import BackupSchema, DetailSchema
from src.services.dependencies import ApplicationManagementServiceDep, BackupServiceDep


api = APIRouter(
    prefix="/backup",
    tags=["Application Backup Management"],
    dependencies=[Depends(PermissionValidator(admin_route=True))],
)


@api.get(
    "/restore-to-backup", status_code=status.HTTP_200_OK, response_model=BackupSchema
)
def get_backup_for_application_to_restore_to_on_restart(
    service: ApplicationManagementServiceDep,
):
    try:
        return service.get_what_backup_app_will_be_restored_to()

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND

    except ConnectionError:
        raise HTTP_EXC_APP_SEETINGS_UNABLE_TO_FETCH_MODIFY_CONFIG


@api.post(
    "/restore-to-backup/{backup_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=DetailSchema,
)
def set_backup_for_application_to_restore_to_on_restart(
    service: ApplicationManagementServiceDep,
    backup_service: BackupServiceDep,
    backup_id: UUID,
):
    try:
        backup = backup_service.get_by_id(backup_id)
        service.specify_backup_app_will_be_restored_to(backup)

        return DetailSchema(
            detail="Backup successfully established as the restore point"
        )

    except NoResultFound:
        raise HTTP_EXC_BACKUP_NOT_FOUND

    except ConnectionError:
        raise HTTP_EXC_APP_SEETINGS_UNABLE_TO_FETCH_MODIFY_CONFIG


@api.delete(
    "/restore-to-backup",
    status_code=status.HTTP_200_OK,
    response_model=DetailSchema,
)
def unset_backup_for_application_to_restore_to_on_restart(
    service: ApplicationManagementServiceDep,
):
    try:
        service.set_app_will_be_restored_to_no_backup()

        return DetailSchema(detail="Backup successfully removed as the restore point")

    except ConnectionError:
        raise HTTP_EXC_APP_SEETINGS_UNABLE_TO_FETCH_MODIFY_CONFIG
