import uuid
from datetime import date, datetime

from pydantic import BaseModel, model_validator

from src.exc import HTTP_EXC_INVALID_RANK_VALUE, HTTP_EXC_NO_RANK_PROVIDED


class RankingSchema(BaseModel):
    id: uuid.UUID
    personnel_id: uuid.UUID

    day: date
    ranking: int | None

    text_events: str | None = None
    text_notes: str | None = None

    created_at: datetime
    updated_at: datetime


class RankingRequest(BaseModel):
    day: date
    ranking: int

    @model_validator(mode="before")
    def validate_rank(cls, values):
        ranking = values.get("ranking")

        if ranking is None:
            raise HTTP_EXC_NO_RANK_PROVIDED

        ranking = int(ranking)

        if ranking < 0 or ranking > 10:
            raise HTTP_EXC_INVALID_RANK_VALUE

        return values


class RankingNotesRequest(BaseModel):
    day: date

    text_events: str | None = None
    text_notes: str | None = None


class RankingADayRequest(RankingRequest):
    text_events: str | None = None
    text_notes: str | None = None


class RankingListSchema(BaseModel):
    min: date
    max: date

    rankings: list[RankingRequest]


class GetAllRankingsResponse(RankingListSchema):
    pass


class GetRangedRankingsResponse(RankingListSchema):
    pass
