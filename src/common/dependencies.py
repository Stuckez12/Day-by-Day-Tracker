from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from src.common import get_db
from src.services import AuthService, PersonalService, RankingService, TaskService

DBSession = Annotated[Session, Depends(get_db)]


def get_auth_service(db: DBSession) -> PersonalService:
    return AuthService(db)


def get_personal_service(db: DBSession) -> PersonalService:
    return PersonalService(db)


def get_ranking_service(db: DBSession) -> RankingService:
    return RankingService(db)


def get_task_service(db: DBSession) -> TaskService:
    return TaskService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
PersonalServiceDep = Annotated[PersonalService, Depends(get_personal_service)]
RankingServiceDep = Annotated[RankingService, Depends(get_ranking_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
