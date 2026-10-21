from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session, selectinload

from src.enums import BackupStatus
from src.models import BackupModel
from src.schemas import BackupCreate, BackupFilters
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

    def get_backups_query(self, filters: BackupFilters) -> Query[BackupModel]:
        query = self.backup_db.query(BackupModel)

        if filters.is_child is not None:
            is_child = BackupModel.parent_backup_id.is_not(None)
            query = query.filter(is_child if filters.is_child else ~is_child)

        if filters.is_processing is not None:
            is_processing = or_(
                BackupModel.status.in_([BackupStatus.RUNNING, BackupStatus.VERIFYING]),
                BackupModel.celery_id.is_not(None),
            )
            query = query.filter(
                is_processing if filters.is_processing else ~is_processing
            )

        if filters.trigger_method is not None:
            query = query.filter(BackupModel.trigger_method == filters.trigger_method)

        if filters.status is not None:
            query = query.filter(BackupModel.status == filters.status)

        if filters.backup_type is not None:
            query = query.filter(BackupModel.backup_type == filters.backup_type)

        if filters.min_duration is not None:
            query = query.filter(BackupModel.duration >= filters.min_duration)

        if filters.max_duration is not None:
            query = query.filter(BackupModel.duration <= filters.max_duration)

        query = query.order_by(BackupModel.created_at.desc())

        return query

    def create(self, data: BackupCreate) -> BackupModel:
        backup = BackupModel(**data.model_dump())

        self.backup_db.add(backup)
        self.backup_db.commit()
        self.backup_db.refresh(backup)

        return backup
