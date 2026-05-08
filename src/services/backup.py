from fastapi import Response
from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import BackupModel
from src.services.base import BaseDBService


class BackupService(BaseDBService[BackupModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=BackupModel)
