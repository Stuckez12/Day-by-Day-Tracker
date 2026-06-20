import logging
import uuid
from datetime import date

from fastapi import APIRouter, Cookie, HTTPException, Query, status
from sqlalchemy.exc import NoResultFound

from src.common import PersonalServiceDep, RankingServiceDep
from src.schemas import (
    RankingADayRequest,
    RankingNotesRequest,
    RankingRequest,
    RankingSchema,
)


api = APIRouter(prefix="/ranking", tags=["Ranking"])


@api.get("/", status_code=status.HTTP_200_OK)
def get_ranking(
    service: RankingServiceDep,
    personnel_service: PersonalServiceDep,
    personnel_id: uuid.UUID = Cookie(..., include_in_schema=False),
    date: date = Query(default_factory=date.today, title="Date"),
):
    personnel_service.personnel_exists(personnel_id)

    return service.fetch_date(personnel_id, date)


@api.get("/all", status_code=status.HTTP_200_OK)
def get_all_rankings(
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie(..., include_in_schema=False),
):
    return service.get_all_personnel_rankings(personnel_id)


@api.get("/today", status_code=status.HTTP_200_OK)
def get_todays_ranking(
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie(..., include_in_schema=False),
):
    return service.fetch_date(personnel_id, date.today())


@api.put(
    "/",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_a_day(
    request: RankingADayRequest,
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie(..., include_in_schema=False),
):
    logging.info("YAAAAAHHHHHH")
    rank_data = service.fetch_date(personnel_id, request.day)

    return service.rank_a_day(rank_data, request)


@api.put(
    "/rank",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_today(
    request: RankingRequest,
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie(..., include_in_schema=False),
):
    rank_data = service.fetch_date(personnel_id, request.day)

    return service.rank_today(rank_data, request.ranking)


@api.put(
    "/rank/notes",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_date_notes(
    request: RankingNotesRequest,
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie(..., include_in_schema=False),
):
    try:
        rank = service.get_by_date(personnel_id, request.day)

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified date's rank not found",
        )

    return service.record_day_notes(rank, request)
