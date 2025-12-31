import uuid

from datetime import date
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.models import RankerModel
from backend.services.base import BaseDBService


class RankingService(BaseDBService[RankerModel]):
    model = RankerModel

    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_date(self, personnel_id: uuid.UUID, date: date):
        return (
            self.db.query(RankerModel)
            .filter(
                RankerModel.personal_id == personnel_id,
                RankerModel.day == date,
            )
            .one()
        )

    def insert_new_date(self, personnel_id: uuid.UUID, date: date):
        row = RankerModel(
            personal_id=personnel_id,
            day=date,
            ranking=None,
        )

        self.add(row)
        self.db.commit()

        return self.get_by_date(personnel_id, date)

    def fetch_date(self, personnel_id: str, date: date):
        try:
            return self.get_by_date(personnel_id, date)

        except NoResultFound:
            return self.insert_new_date(personnel_id, date)

    def rank_day(self, rank_row: RankerModel, set_rank: int):
        rank_row.ranking = set_rank

        self.db.commit()
        self.db.refresh(rank_row)

        return rank_row
