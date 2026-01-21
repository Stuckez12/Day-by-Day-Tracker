import uuid

from datetime import date
from fastapi import APIRouter, status, Cookie, Query

from backend.common import PersonalServiceDep, RankingServiceDep
from backend.schemas import RankingRequest, RankingSchema


api = APIRouter(prefix="/ranking", tags=["Ranking"])


@api.get("/", status_code=status.HTTP_200_OK)
def get_ranking(
    service: RankingServiceDep,
    personnel_service: PersonalServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
    date: date = Query(default_factory=date.today, title="Date"),
):
    personnel_service.personnel_exists(personnel_id)

    return service.fetch_date(personnel_id, date)


@api.get("/all", status_code=status.HTTP_200_OK)
def get_all_rankings(
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
):
    return service.get_all_personnel_rankings(personnel_id)


@api.get("/today", status_code=status.HTTP_200_OK)
def get_todays_ranking(
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
):
    return service.fetch_date(personnel_id, date.today())


@api.put(
    "/rank",
    response_model=RankingSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def rank_day(
    request: RankingRequest,
    service: RankingServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
):
    rank_data = service.fetch_date(personnel_id, request.day)

    return service.rank_day(rank_data, request.ranking)
