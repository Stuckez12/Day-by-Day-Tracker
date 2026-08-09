from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import NoResultFound

from src.common import CurrentPersonnel, RankingServiceDep
from src.schemas import (
    DateRangeRequest,
    RankingADayRequest,
    RankingNotesRequest,
    RankingRequest,
    RankingSchema,
)


api = APIRouter(prefix="/ranking", tags=["Ranking"])


@api.get("", response_model=RankingSchema, status_code=status.HTTP_200_OK)
def get_ranking(
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
    date: date = Query(default_factory=date.today, title="Date"),
):
    return service.fetch_date(personnel.id, date)


@api.get("/all", response_model=list[RankingSchema], status_code=status.HTTP_200_OK)
def get_all_rankings(
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
):
    return service.get_all_personnel_rankings(personnel.id)


@api.get("/range", response_model=list[RankingSchema], status_code=status.HTTP_200_OK)
def get_ranking_range(
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
    date_range: Annotated[DateRangeRequest, Depends()],
):
    return service.get_ranking_range(personnel.id, date_range)


@api.get("/today", response_model=RankingSchema, status_code=status.HTTP_200_OK)
def get_todays_ranking(
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
):
    return service.fetch_date(personnel.id, date.today())


@api.put(
    "",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_a_day(
    request: RankingADayRequest,
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
):
    rank_data = service.fetch_date(personnel.id, request.day)

    return service.rank_a_day(rank_data, request)


@api.put(
    "/rank",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_today(
    request: RankingRequest,
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
):
    request.day = date.today()
    rank_data = service.fetch_date(personnel.id, request.day)

    return service.rank_today(rank_data, request.ranking)


@api.put(
    "/rank/notes",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_date_notes(
    request: RankingNotesRequest,
    service: RankingServiceDep,
    personnel: CurrentPersonnel,
):
    try:
        rank = service.get_by_date(personnel.id, request.day)

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified date's rank not found",
        )

    return service.record_day_notes(rank, request)
