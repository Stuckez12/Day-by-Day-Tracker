from datetime import date
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from src.models import PersonnelModel, RankerModel
from src.services import RankingService


class TestGetRankRankerService:
    def test_success(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        rank = test_ranking_service.get_by_date(
            test_ranker.personal_id, test_ranker.day
        )

        assert rank == test_ranker

    def test_invalid_personnel(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        invalid_personnel_id = UUID("12345678-1234-5678-1234-567812345678")

        with pytest.raises(NoResultFound):
            test_ranking_service.get_by_date(invalid_personnel_id, test_ranker.day)

    def test_invalid_date(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        invalid_date = date(1, 1, 1)

        with pytest.raises(NoResultFound):
            test_ranking_service.get_by_date(test_ranker.personal_id, invalid_date)


class TestInsertRankRankerService:
    def test_success(
        self,
        test_session: Session,
        test_ranking_service: RankingService,
        test_personnel: PersonnelModel,
        test_date_today: date,
    ):
        rank = test_ranking_service.insert_new_date(test_personnel.id, test_date_today)

        assert rank.personal_id == test_personnel.id
        assert rank.day == test_date_today
        assert rank.ranking is None

        test_session.delete(rank)
        test_session.commit()

    def test_invalid_personnel_id(
        self,
        test_session: Session,
        test_ranking_service: RankingService,
        test_date_today: date,
    ):
        invalid_personnel_id = UUID("12345678-1234-5678-1234-567812345678")

        with pytest.raises(IntegrityError):
            test_ranking_service.insert_new_date(invalid_personnel_id, test_date_today)

        test_session.rollback()


class TestFetchRankRankerService:
    def test_success(
        self,
        test_ranking_service: RankingService,
        test_ranker: RankerModel,
    ):
        rank = test_ranking_service.fetch_date(test_ranker.personal_id, test_ranker.day)

        assert rank == test_ranker

    def test_not_found(
        self,
        test_session: Session,
        test_ranking_service: RankingService,
        test_personnel: PersonnelModel,
        test_date_today: date,
    ):
        rank = test_ranking_service.fetch_date(test_personnel.id, test_date_today)

        assert rank.personal_id == test_personnel.id
        assert rank.day == test_date_today
        assert rank.ranking is None

        test_session.delete(rank)
        test_session.commit()


class TestRankTodayRankerService:
    def test_success(
        self, test_ranking_service: RankingService, test_ranker: RankerModel
    ):
        ranked = test_ranking_service.rank_today(test_ranker, 10)
        rank_instance = test_ranking_service.get_by_id(test_ranker.id)

        assert ranked.ranking == 10
        assert rank_instance
        assert rank_instance.ranking == 10
