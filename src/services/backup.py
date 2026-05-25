from sqlalchemy.orm import Session

from src.models import BackupModel
from src.services.base import BaseDBService


class BackupService(BaseDBService[BackupModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=BackupModel)
