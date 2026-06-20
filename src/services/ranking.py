import uuid
from datetime import date

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.models import RankerModel
from src.schemas import RankingADayRequest, RankingNotesRequest, RankingSchema
from src.services.base import BaseDBService


class RankingService(BaseDBService[RankerModel]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=RankerModel)

    def get_by_date(self, personnel_id: uuid.UUID, date: date) -> RankerModel:
        return (
            self.db.query(RankerModel)
            .filter(
                RankerModel.personal_id == personnel_id,
                RankerModel.day == date,
            )
            .one()
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
        try:
            return self.get_by_date(personnel_id, date)

        except NoResultFound:
            return self.insert_new_date(personnel_id, date)

    def rank_a_day(self, rank_row: RankerModel, data: RankingADayRequest):
        rank_row.ranking = data.ranking
        rank_row.text_events = data.text_events
        rank_row.text_notes = data.text_notes

        self.db.commit()
        self.db.refresh(rank_row)

        return RankingSchema(**rank_row.to_dict())

    def rank_today(self, rank_row: RankerModel, set_rank: int):
        rank_row.ranking = set_rank

        self.db.commit()
        self.db.refresh(rank_row)

        return RankingSchema(**rank_row.to_dict())

    def record_day_notes(self, rank_row: RankerModel, notes: RankingNotesRequest):
        rank_row.text_events = notes.text_events
        rank_row.text_notes = notes.text_notes

        self.db.commit()
        self.db.refresh(rank_row)

        return RankingSchema(**rank_row.to_dict())
