from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from src.models import BackupModel
from src.schemas import (
    BackupCreate,
)
from src.services.base import BaseDBService


class BackupService(BaseDBService[BackupModel]):
    def __init__(self, db: Session, backup_db: Session) -> None:
        super().__init__(db=db, model=BackupModel)

        self.backup_db = backup_db

    def get_by_backup_id(self, backup_id: UUID) -> BackupModel:
        return (
            self.backup_db.query(BackupModel)
            .filter(BackupModel.id == backup_id)
            .options(selectinload(BackupModel.meta))
            .one()
        )

    def get_by_task_id(self, task_id: UUID) -> BackupModel:
        return (
            self.backup_db.query(BackupModel)
            .filter(BackupModel.celery_id == task_id)
            .options(selectinload(BackupModel.meta))
            .one()
        )

    def get_all(self) -> list[BackupModel]:
        return (
            self.backup_db.query(BackupModel)
            .order_by(BackupModel.created_at.desc())
            .all()
        )

    def create(self, data: BackupCreate) -> BackupModel:
        backup = BackupModel(**data.model_dump())

        self.backup_db.add(backup)
        self.backup_db.commit()
        self.backup_db.refresh(backup)

        return backup
