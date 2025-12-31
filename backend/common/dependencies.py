from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

from backend.common import get_db
from backend.services import PersonalService, RankingService


def get_personal_service(db: Session = Depends(get_db)) -> PersonalService:
    return PersonalService(db)


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    return RankingService(db)


PersonalServiceDep = Annotated[PersonalService, Depends(get_personal_service)]
RankingServiceDep = Annotated[RankingService, Depends(get_ranking_service)]
