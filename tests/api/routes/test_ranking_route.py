import uuid
from datetime import date, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models import PersonalModel, RankerModel
from src.schemas import RankingSchema


class TestGetRankingRoute:
    def test_success(
        self,
        test_client_user_session: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_client_user_session.get("/ranking")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker.to_dict(clean=True)

    def test_specified_date(
        self,
        test_client_user_session: TestClient,
        test_ranker_set_date: RankerModel,
    ):
        result = test_client_user_session.get(
            f"/ranking?date={test_ranker_set_date.day}"
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker_set_date.to_dict(clean=True)

    def test_no_personnel_cookie(
        self,
        test_app: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_app.get(f"/ranking?date={test_ranker.day}")
        assert result.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetAllRankingRoute:
    def test_success(
        self,
        test_client_user_session: TestClient,
        test_ranker: RankerModel,
        test_ranker_none: RankerModel,
        test_ranker_set_date: RankerModel,
    ):
        result = test_client_user_session.get("/ranking/all")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data[0] == test_ranker.to_dict(clean=True)
        assert data[1] == test_ranker_none.to_dict(clean=True)
        assert data[2] == test_ranker_set_date.to_dict(clean=True)

    def test_no_personnel_cookie(self, test_app: TestClient):
        result = test_app.get("/ranking/all")
        assert result.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetRankingRangeRoute:
    def test_success(
        self,
        test_session: Session,
        test_date_today: date,
        test_client_user_session: TestClient,
        test_ranker: RankerModel,
        test_ranker_none: RankerModel,
        test_ranker_set_date: RankerModel,
    ):
        test_ranker_none.day = test_date_today - timedelta(days=0.5)
        test_session.commit()

        result = test_client_user_session.get(
            "/ranking/range",
            params={
                "min_date": str(test_date_today - timedelta(days=1)),
                "max_date": str(test_date_today + timedelta(days=1)),
            },
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert len(data) == 2
        assert all(RankingSchema.model_validate(ranker) for ranker in data)
        assert any(ranker["id"] == str(test_ranker.id) for ranker in data)
        assert any(ranker["id"] == str(test_ranker_none.id) for ranker in data)


class TestGetTodaysRankRoute:
    def test_success(
        self,
        test_client_user_session: TestClient,
        test_ranker: RankerModel,
    ):
        result = test_client_user_session.get("/ranking/today")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == test_ranker.to_dict(clean=True)

    def test_create_new_record_success(
        self,
        test_session: Session,
        test_client_user_session: TestClient,
        test_date_today: date,
    ):
        result = test_client_user_session.get("/ranking/today")
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

    def test_no_personnel_cookie(self, test_app: TestClient):
        result = test_app.get("/ranking/today")
        assert result.status_code == status.HTTP_401_UNAUTHORIZED


class TestFullRankDayRoute:
    pass


class TestRankADayRoute:
    def test_success(
        self,
        test_client_user_session: TestClient,
        test_date_today: date,
        test_session_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        result = test_client_user_session.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert RankingSchema.model_validate(data)
        assert data["personal_id"] == str(test_session_personnel.id)
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["ranking"] == 10

    def test_create_new_record_success(
        self,
        test_session: Session,
        test_client_user_session: TestClient,
        test_date_today: date,
        test_session_personnel: PersonalModel,
    ):
        result = test_client_user_session.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        try:
            assert RankingSchema(**data)
            assert data["personal_id"] == str(test_session_personnel.id)
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

    def test_rerank_day(
        self,
        test_client_user_session: TestClient,
        test_date_today: date,
        test_session_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        result = test_client_user_session.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_202_ACCEPTED

        data = result.json()
        assert RankingSchema.model_validate(data)
        assert data["personal_id"] == str(test_session_personnel.id)
        assert data["day"] == test_date_today.strftime("%Y-%m-%d")
        assert data["ranking"] == 10

    def test_rejected_over_two_weeks_old(
        self,
        test_session: Session,
        test_client_user_session: TestClient,
        test_date_today: date,
        test_session_personnel: PersonalModel,
        test_ranker_none: RankerModel,
    ):
        test_ranker_none.day = test_date_today - timedelta(days=30)
        test_session.commit()

        json_data = {"day": test_ranker_none.day.strftime("%Y-%m-%d"), "ranking": 10}
        result = test_client_user_session.put(
            "/ranking",
            json=json_data,
        )
        assert result.status_code == status.HTTP_403_FORBIDDEN

        data = result.json()
        assert (
            data["detail"] == "You cannot modify a ranked day more than two weeks old"
        )

    def test_no_personnel_cookie(
        self,
        test_app: TestClient,
        test_date_today: date,
    ):
        result = test_app.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 10},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_day_provided(self, test_client_user_session: TestClient):
        result = test_client_user_session.put("/ranking/rank", json={"ranking": 10})
        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_no_ranking_provided(
        self,
        test_client_user_session: TestClient,
        test_date_today: date,
    ):
        result = test_client_user_session.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d")},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "A rank must be provided"

    def test_ranking_too_low(
        self,
        test_client_user_session: TestClient,
        test_date_today: date,
    ):
        result = test_client_user_session.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": -1},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Ranking must be between 0 and 10"

    def test_ranking_too_high(
        self,
        test_client_user_session: TestClient,
        test_date_today: date,
    ):
        result = test_client_user_session.put(
            "/ranking/rank",
            json={"day": test_date_today.strftime("%Y-%m-%d"), "ranking": 11},
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Ranking must be between 0 and 10"


class TestRankNotesRoute:
    def test_success(
        self,
        test_client_user_session: TestClient,
        test_date_today: date,
        test_ranker: RankerModel,
    ):
        result = test_client_user_session.put(
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

    def test_no_personnel_cookie(
        self,
        test_app: TestClient,
        test_date_today: date,
    ):
        result = test_app.put(
            "/ranking/rank/notes",
            json={"day": test_date_today.strftime("%Y-%m-%d")},
        )
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_rank_not_found(self, test_client_user_session: TestClient):
        result = test_client_user_session.put(
            "/ranking/rank/notes", json={"day": "2004-04-04"}
        )
        assert result.status_code == status.HTTP_404_NOT_FOUND

        response = result.json()
        assert "detail" in response
        assert response["detail"] == "Specified date's rank not found"
