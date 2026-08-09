from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.common import get_db
from src.services import AuthService, PersonnelService, RankingService, TaskService


DBSession = Annotated[Session, Depends(get_db)]


def get_auth_service(db: DBSession) -> PersonnelService:
    return AuthService(db)


def get_personnel_service(db: DBSession) -> PersonnelService:
    return PersonnelService(db)


def get_ranking_service(db: DBSession) -> RankingService:
    return RankingService(db)


def get_task_service(db: DBSession) -> TaskService:
    return TaskService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
PersonnelServiceDep = Annotated[PersonnelService, Depends(get_personnel_service)]
RankingServiceDep = Annotated[RankingService, Depends(get_ranking_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
