import uuid

from datetime import date, datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator


class RankingSchema(BaseModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    personal_id: uuid.UUID
    day: date
    ranking: int | None


class RankingRequest(BaseModel):
    day: date
    ranking: int

    @model_validator(mode="before")
    def validate_rank(cls, values):
        ranking = values.get("ranking")

        if ranking is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A rank must be provided",
            )

        if ranking < 0 or ranking > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ranking must be between 0 and 10",
            )

        return values


class RankingListSchema(BaseModel):
    min: date
    max: date
    rankings: list[RankingRequest]


class GetAllRankingsResponse(RankingListSchema):
    pass


class GetRangedRankingsResponse(RankingListSchema):
    pass
