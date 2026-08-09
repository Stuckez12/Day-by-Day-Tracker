from src.common.database import get_db
from src.common.dependencies import (
    AuthServiceDep,
    DBSession,
    PersonnelServiceDep,
    RankingServiceDep,
    TaskServiceDep,
)
from src.common.security import CurrentPersonnelID
