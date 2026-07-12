import uuid
from datetime import date, datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models import PersonalModel, RankerModel
from src.schemas import RankingSchema


class TestRankingRoute:
    def test_get_ranking_default(
        self,
        test_client_user: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_client_user.get("/ranking")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker.to_dict(clean=True)

    def test_get_ranking_w_specified_date(
        self,
        test_client_user: TestClient,
        test_ranker_set_date: RankerModel,
    ):
        result = test_client_user.get(f"/ranking?date={test_ranker_set_date.day}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker_set_date.to_dict(clean=True)

    def test_get_ranking_invalid_personnel_cookie(
        self,
        test_client: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_client.get(f"/ranking?date={test_ranker.day}")
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_all_personnel_rankings(
        self,
        test_client_user: TestClient,
        test_ranker: RankerModel,
        test_ranker_none: RankerModel,
        test_ranker_set_date: RankerModel,
    ):
        result = test_client_user.get("/ranking/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data[0] == test_ranker.to_dict(clean=True)
        assert data[1] == test_ranker_none.to_dict(clean=True)
        assert data[2] == test_ranker_set_date.to_dict(clean=True)

    def test_get_all_personnel_rankings_no_personnel_cookie(
        self, test_client: TestClient
    ):
        result = test_client.get("/ranking/all")
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_todays_personnel_rankings(
        self,
        test_client_user: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_client_user.get("/ranking/today")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker.to_dict(clean=True)

    def test_get_todays_personnel_rankings_not_in_database(
        self,
        test_session: Session,
        test_client_user: TestClient,
        test_date_today: date,
    ):
        result = test_client_user.get("/ranking/today")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()

        try:
            assert uuid.UUID(data["id"])
            assert datetime.fromisoformat(data["created_at"])
            assert datetime.fromisoformat(data["updated_at"])
            assert uuid.UUID(data["personal_id"])
            assert data["day"] == test_date_today.strftime("%Y-%m-%d")
            assert data["ranking"] is None

        finally:
            ranking = (
                test_session.query(RankerModel)
                .filter(RankerModel.id == uuid.UUID(data["id"]))
                .one()
            )

            test_session.delete(ranking)
            test_session.commit()

    def test_get_todays_personnel_rankings_no_personnel_cookie(
        self, test_client: TestClient
    ):
        result = test_client.get("/ranking/today")
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_rank_day(
        self,
        test_client_user: TestClient,
        test_date_today: date,
        test_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        result = test_client_user.put(
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
        test_client_user: TestClient,
        test_date_today: date,
        test_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        result = test_client_user.put(
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
        test_session: Session,
        test_client_user: TestClient,
        test_date_today: date,
        test_personnel: PersonalModel,
    ):
        result = test_client_user.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        try:
            assert RankingSchema(**data)
            assert data["personal_id"] == str(test_personnel.id)
            assert data["day"] == test_date_today.strftime("%Y-%m-%d")
            assert data["ranking"] == 10

        finally:
            ranking = (
                test_session.query(RankerModel)
                .filter(RankerModel.id == data["id"])
                .one()
            )

            test_session.delete(ranking)
            test_session.commit()

    def test_rank_day_no_personnel_cookie(
        self,
        test_client: TestClient,
        test_date_today: date,
    ):
        result = test_client.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_rank_day_no_day_provided(self, test_client_user: TestClient):
        result = test_client_user.put("/ranking/rank", json={"ranking": 10})
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_rank_day_no_ranking_provided(
        self,
        test_client_user: TestClient,
        test_date_today: date,
    ):
        result = test_client_user.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d")},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "A rank must be provided"

    def test_rank_day_ranking_too_low(
        self,
        test_client_user: TestClient,
        test_date_today: date,
    ):
        result = test_client_user.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": -1},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Ranking must be between 0 and 10"

    def test_rank_day_ranking_too_high(
        self,
        test_client_user: TestClient,
        test_date_today: date,
    ):
        result = test_client_user.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 11},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Ranking must be between 0 and 10"

    def test_rank_date_notes(
        self,
        test_client_user: TestClient,
        test_date_today: date,
        test_ranker: RankerModel,
    ):
        result = test_client_user.put(
            "/ranking/rank/notes",
            json={
                "day": test_date_today.strftime("%Y-%m-%d"),
                "text_events": "Event test",
                "text_notes": "Note test",
            },
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert RankingSchema(**data)
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["text_events"] == "Event test"
        assert data["text_notes"] == "Note test"

    def test_rank_date_notes_no_personnel_cookie(
        self,
        test_client: TestClient,
        test_date_today: date,
    ):
        result = test_client.put(
            "/ranking/rank/notes",
            json={"day": test_date_today.strftime("%Y-%m-%d")},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_rank_date_notes_not_found_rank(self, test_client_user: TestClient):
        result = test_client_user.put("/ranking/rank/notes", json={"day": "2004-04-04"})
        assert result.status_code == status.HTTP_404_NOT_FOUND

        response = result.json()
        assert "detail" in response
        assert response["detail"] == "Specified date's rank not found"
