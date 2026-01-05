import uuid

from datetime import date
from pydantic import BaseModel, model_validator


class RankingSchema(BaseModel):
    personal_id: uuid.UUID
    day: date
    ranking: int | None


class RankingRequest(BaseModel):
    day: date
    ranking: int

    @model_validator(mode="before")
    def validate_rank(cls, values):
        ranking = values.get("ranking")

        if ranking < 0 or ranking > 10:
            raise ValueError("Ranking must be between 0 and 10")

        return values


class RankingListSchema(BaseModel):
    min: date
    max: date
    rankings: list[RankingRequest]


class GetAllRankingsResponse(RankingListSchema):
    pass


class GetRangedRankingsResponse(RankingListSchema):
    pass
