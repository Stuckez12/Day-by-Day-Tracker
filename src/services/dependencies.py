from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core import get_backup_db, get_db
from src.services import (
    ApplicationManagementService,
    AuthService,
    BackupSchedulerService,
    BackupService,
    PersonnelService,
    RankingService,
    TaskService,
)


DBSession = Annotated[Session, Depends(get_db)]
BackupDBSession = Annotated[Session, Depends(get_backup_db)]


def get_app_management_service(
    db: DBSession, backup_service: BackupServiceDep
) -> ApplicationManagementService:
    return ApplicationManagementService(db, backup_service)


def get_auth_service(db: DBSession) -> PersonnelService:
    return AuthService(db)


def get_backup_service(db: DBSession, backup_db: BackupDBSession) -> BackupService:
    return BackupService(db=db, backup_db=backup_db)


def get_backup_scheduler_service(
    db: DBSession, backup_db: BackupDBSession
) -> BackupSchedulerService:
    return BackupSchedulerService(db=db, backup_db=backup_db)


def get_personnel_service(db: DBSession) -> PersonnelService:
    return PersonnelService(db)


def get_ranking_service(db: DBSession) -> RankingService:
    return RankingService(db)


def get_task_service(db: DBSession) -> TaskService:
    return TaskService(db)


ApplicationManagementServiceDep = Annotated[
    ApplicationManagementService, Depends(get_app_management_service)
]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
BackupServiceDep = Annotated[BackupService, Depends(get_backup_service)]
BackupSchedulerServiceDep = Annotated[
    BackupSchedulerService, Depends(get_backup_scheduler_service)
]
PersonnelServiceDep = Annotated[PersonnelService, Depends(get_personnel_service)]
RankingServiceDep = Annotated[RankingService, Depends(get_ranking_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
