import pytest

from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from backend.models import PersonalModel, RankerModel
from backend.schemas import (
    InvalidSchema,
)
from backend.services import RankingService


class TestRankerService:
    def test_get_rank_by_date_success(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        rank = test_ranking_service.get_by_date(
            test_ranker.personal_id, test_ranker.day
        )

        assert rank == test_ranker

    def test_get_rank_by_date_invalid_personnel(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        invalid_personnel_id = UUID("12345678-1234-5678-1234-567812345678")

        rank = test_ranking_service.get_by_date(invalid_personnel_id, test_ranker.day)

        assert rank is None

    def test_get_rank_by_date_invalid_date(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        invalid_date = date(1, 1, 1)
        rank = test_ranking_service.get_by_date(test_ranker.personal_id, invalid_date)

        assert rank is None

    def test_insert_new_ranked_date_success(
        self,
        test_session: Session,
        test_ranking_service: RankingService,
        test_personnel: PersonalModel,
        test_date_today: date,
    ):
        rank = test_ranking_service.insert_new_date(test_personnel.id, test_date_today)

        assert rank.personal_id == test_personnel.id
        assert rank.day == test_date_today
        assert rank.ranking is None

        test_session.delete(rank)
        test_session.commit()

    def test_insert_new_ranked_date_invalid_personnel_id(
        self,
        test_ranking_service: RankingService,
        test_date_today: date,
    ):
        invalid_personnel_id = UUID("12345678-1234-5678-1234-567812345678")

        with pytest.raises(IntegrityError):
            test_ranking_service.insert_new_date(invalid_personnel_id, test_date_today)

    def test_fetch_date_date_exists(
        self,
        test_ranking_service: RankingService,
        test_ranker: RankerModel,
    ):
        rank = test_ranking_service.fetch_date(test_ranker.personal_id, test_ranker.day)

        assert rank == test_ranker

    def test_fetch_date_date_does_not_exists(
        self,
        test_session: Session,
        test_ranking_service: RankingService,
        test_personnel: PersonalModel,
        test_date_today: date,
    ):
        rank = test_ranking_service.fetch_date(test_personnel.id, test_date_today)

        assert rank.personal_id == test_personnel.id
        assert rank.day == test_date_today
        assert rank.ranking is None

        test_session.delete(rank)
        test_session.commit()

    def test_rank_day_success(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        ranked = test_ranking_service.rank_day(test_ranker, 10)
        rank_instance = test_ranking_service.get_by_id(test_ranker.id)

        assert ranked.ranking == 10
        assert rank_instance.ranking == 10
