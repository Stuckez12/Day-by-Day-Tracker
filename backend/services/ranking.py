import uuid

from datetime import date
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.models import RankerModel
from backend.services.base import BaseDBService
from backend.schemas import RankingSchema


class RankingService(BaseDBService[RankerModel]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=RankerModel)

    def get_by_date(self, personnel_id: uuid.UUID, date: date) -> RankerModel | None:
        return (
            self.db.query(RankerModel)
            .filter(
                RankerModel.personal_id == personnel_id,
                RankerModel.day == date,
            )
            .first()
        )

    def get_all_personnel_rankings(self, personnel_id: uuid.UUID):
        return (
            self.db.query(RankerModel)
            .filter(RankerModel.personal_id == personnel_id)
            .order_by(RankerModel.day.desc())
            .all()
        )

    def insert_new_date(self, personnel_id: uuid.UUID, date: date) -> RankerModel:
        row = RankerModel(
            personal_id=personnel_id,
            day=date,
            ranking=None,
        )

        self.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def fetch_date(self, personnel_id: uuid.UUID, date: date) -> RankerModel:
        row = self.get_by_date(personnel_id, date)

        if row is None:
            return self.insert_new_date(personnel_id, date)

        return row

    def rank_day(self, rank_row: RankerModel, set_rank: int):
        rank_row.ranking = set_rank

        self.db.commit()
        self.db.refresh(rank_row)

        return RankingSchema(**rank_row.to_dict())
