from src.schemas.auth import LogInRequest
from src.schemas.common import DateRequest, DateRangeRequest, InvalidSchema
from src.schemas.personal import (
    CreatePersonnelRequest,
    PersonnelSchema,
    SlimPersonnelSchema,
    SelectPersonnelRequest,
    UpdatePersonnelDetailsRequest,
    UpdatePersonnelEmailRequest,
    UpdatePersonnelPasswordRequest,
)
from src.schemas.ranking import (
    GetAllRankingsResponse,
    GetRangedRankingsResponse,
    RankingListSchema,
    RankingRequest,
    RankingSchema,
)
