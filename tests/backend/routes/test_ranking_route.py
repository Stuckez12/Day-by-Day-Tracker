import pytest
import uuid

from datetime import date, datetime
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import PersonalModel, RankerModel
from backend.schemas import RankingSchema

from tests.backend.constants import INVALID_PERSONNEL_ID


class TestRankingRoute:
    def test_get_ranking_default(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
        test_ranker: RankerModel,
    ):
        result = test_client_v1.get("/ranking")
        data = result.json()
        print(data)
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker.to_dict(clean=True)

    def test_get_ranking_w_specified_date(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
        test_ranker_set_date: RankerModel,
    ):
        result = test_client_v1.get(f"/ranking?date={test_ranker_set_date.day}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker_set_date.to_dict(clean=True)

    @pytest.mark.skip("FIXME: Test uses cookie from previous test")
    def test_get_ranking_invalid_personnel_cookie(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_personnel: PersonalModel,
        test_ranker: RankerModel,
    ):
        result = test_client_v1.get(f"/ranking?date={test_ranker.day}")
        # assert result.status_code == status.HTTP_200_OK

        data = result.json()
        print(data)

        assert data["detail"] == f"Personnel {INVALID_PERSONNEL_ID} not found"

    def test_get_all_personnel_rankings(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_ranker: RankerModel,
        test_ranker_none: RankerModel,
        test_ranker_set_date: RankerModel,
    ):
        result = test_client_v1.get("/ranking/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data[0] == test_ranker.to_dict(clean=True)
        assert data[1] == test_ranker_none.to_dict(clean=True)
        assert data[2] == test_ranker_set_date.to_dict(clean=True)

    @pytest.mark.skip("FIXME: Test uses cookie from previous test")
    def test_get_all_personnel_rankings_no_personnel_cookie(
        self, test_client_v1: TestClient
    ):
        result = test_client_v1.get("/ranking/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        print(data)

        assert False

    def test_get_todays_personnel_rankings(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_client_v1.get("/ranking/today")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker.to_dict(clean=True)

    def test_get_todays_personnel_rankings_not_in_database(
        self,
        test_session: Session,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_date_today: date,
    ):
        result = test_client_v1.get("/ranking/today")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert uuid.UUID(data["id"])
        assert datetime.fromisoformat(data["created_at"])
        assert datetime.fromisoformat(data["updated_at"])
        assert uuid.UUID(data["personal_id"])
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["ranking"] is None

        rank = (
            test_session.query(RankerModel)
            .filter(RankerModel.id == uuid.UUID(data["id"]))
            .one()
        )

        test_session.delete(rank)
        test_session.commit()

    @pytest.mark.skip("FIXME: Test uses cookie from previous test")
    def test_get_todays_personnel_rankings_no_personnel_cookie(
        self, test_client_v1: TestClient
    ):
        result = test_client_v1.get("/ranking/today")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        print(data)

        assert False

    def test_rank_day(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_date_today: date,
        test_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        result = test_client_v1.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert RankingSchema(**data)
        assert data["personal_id"] == str(test_personnel.id)
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["ranking"] == 10

    def test_rank_day_rerank_day(
        self,
        test_set_cookies: None,
        test_client_v1: TestClient,
        test_date_today: date,
        test_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        result = test_client_v1.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert RankingSchema(**data)
        assert data["personal_id"] == str(test_personnel.id)
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["ranking"] == 10

    def test_rank_day_day_not_in_database(
        self,
        test_set_cookies: None,
        test_session: Session,
        test_client_v1: TestClient,
        test_date_today: date,
        test_personnel: PersonalModel,
    ):
        result = test_client_v1.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert RankingSchema(**data)
        assert data["personal_id"] == str(test_personnel.id)
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["ranking"] == 10

        ranking = (
            test_session.query(RankerModel).filter(RankerModel.id == data["id"]).one()
        )

        test_session.delete(ranking)
        test_session.commit()

    @pytest.mark.skip("FIXME: Test uses cookie from previous test")
    def test_rank_day_no_personnel_cookie(self, test_client_v1: TestClient):
        result = test_client_v1.put("/ranking/rank")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        print(data)

        assert False

    def test_rank_day_no_day_provided(
        self, test_set_cookies: None, test_client_v1: TestClient
    ):
        result = test_client_v1.put("/ranking/rank", json={"ranking": 10})
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_rank_day_no_ranking_provided(
        self, test_set_cookies: None, test_client_v1: TestClient, test_date_today: date
    ):
        result = test_client_v1.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d")},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "A rank must be provided"

    def test_rank_day_ranking_too_low(
        self, test_set_cookies: None, test_client_v1: TestClient, test_date_today: date
    ):
        result = test_client_v1.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": -1},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Ranking must be between 0 and 10"

    def test_rank_day_ranking_too_high(
        self, test_set_cookies: None, test_client_v1: TestClient, test_date_today: date
    ):
        result = test_client_v1.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 11},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Ranking must be between 0 and 10"
