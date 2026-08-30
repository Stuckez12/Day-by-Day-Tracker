import uuid
from datetime import date, timedelta

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.exc import HTTP_EXC_RANK_OLDER_THAN_TWO_WEEKS
from src.models import RankerModel
from src.schemas import (
    DateRangeRequest,
    RankingADayRequest,
    RankingNotesRequest,
    RankingSchema,
)
from src.services.base import BaseDBService


class RankingService(BaseDBService[RankerModel]):
    def __init__(self, db: Session):
        super().__init__(db=db, model=RankerModel)

    def get_by_date(self, personnel_id: uuid.UUID, date: date) -> RankerModel:
        return (
            self.db.query(RankerModel)
            .filter(
                RankerModel.personnel_id == personnel_id,
                RankerModel.day == date,
            )
            .one()
        )

    def get_all_personnel_rankings(self, personnel_id: uuid.UUID):
        return (
            self.db.query(RankerModel)
            .filter(RankerModel.personnel_id == personnel_id)
            .order_by(RankerModel.day.desc())
            .all()
        )

    def get_ranking_range(self, personnel_id: uuid.UUID, range: DateRangeRequest):
        return (
            self.db.query(RankerModel)
            .filter(
                RankerModel.personnel_id == personnel_id,
                RankerModel.day >= range.min_date,
                RankerModel.day <= range.max_date,
            )
            .order_by(RankerModel.day.desc())
            .all()
        )

    def insert_new_date(self, personnel_id: uuid.UUID, date: date) -> RankerModel:
        row = RankerModel(
            personnel_id=personnel_id,
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

    def can_modify_rank(self, rank: RankerModel):
        if rank.day + timedelta(days=14) < date.today():
            raise HTTP_EXC_RANK_OLDER_THAN_TWO_WEEKS

    def rank_a_day(self, rank: RankerModel, data: RankingADayRequest):
        self.can_modify_rank(rank)

        rank.ranking = data.ranking
        rank.text_events = data.text_events
        rank.text_notes = data.text_notes

        self.db.commit()
        self.db.refresh(rank)

        return RankingSchema(**rank.to_dict())

    def rank_today(self, rank: RankerModel, set_rank: int) -> RankingSchema:
        rank.ranking = set_rank

        self.db.commit()
        self.db.refresh(rank)

        return RankingSchema(**rank.to_dict())

    def record_day_notes(self, rank: RankerModel, notes: RankingNotesRequest):
        self.can_modify_rank(rank)

        rank.text_events = notes.text_events
        rank.text_notes = notes.text_notes

        self.db.commit()
        self.db.refresh(rank)

        return RankingSchema(**rank.to_dict())
