from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Query, Session, aliased, selectinload
from sqlalchemy.sql.expression import literal

from src.core.data_structure import LinkedList
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

    def get_backup_chain(self, backup: BackupModel) -> LinkedList:
        rec = self.backup_db.query(
            literal(backup.parent_backup_id).label("parent_backup_id")
        ).cte(recursive=True, name="recursive_backups")

        ralias = aliased(rec, name="R")
        lalias = aliased(BackupModel, name="L")

        rec = rec.union_all(
            select(lalias.parent_backup_id).join(
                ralias, ralias.c.parent_backup_id == lalias.id
            )
        )

        backup_chain_list = (
            self.backup_db.query(BackupModel)
            .join(rec, BackupModel.id == rec.c.parent_backup_id)
            .all()
        )

        backup_chain = LinkedList.create_from_ordered_list(
            ordered_list=backup_chain_list
        )

        return backup_chain
