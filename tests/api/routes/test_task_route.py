from datetime import datetime, timedelta
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from src.models import TaskModel
from src.schemas import TaskSchema


class TestTaskRoute:
    def test_get_task_paginated_via_task_id(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/paginated?task_id={test_task_1.task_id}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 1
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_1
        )

    def test_get_task_paginated_via_name(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/paginated?name=task2")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 2
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_2
        )
        assert TaskSchema.model_validate(data["items"][1]) == TaskSchema.model_validate(
            test_task_3
        )

    def test_get_task_paginated_via_task_status(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(
            f"/tasks/paginated?task_status={test_task_2.status}"
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 1
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_2
        )

    def test_get_task_paginated_via_min_retries(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/paginated?min_retries=1")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 2
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_2
        )
        assert TaskSchema.model_validate(data["items"][1]) == TaskSchema.model_validate(
            test_task_3
        )

    def test_get_task_paginated_via_max_retries(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/paginated?max_retries=1")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 2
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_1
        )
        assert TaskSchema.model_validate(data["items"][1]) == TaskSchema.model_validate(
            test_task_3
        )

    def test_get_task_paginated_via_started_at(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(
            f"/tasks/paginated?started_at={test_task_3.started_at}"
        )
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 2
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_2
        )
        assert TaskSchema.model_validate(data["items"][1]) == TaskSchema.model_validate(
            test_task_3
        )

    def test_get_task_paginated_via_ended_at(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/paginated?ended_at={test_task_2.ended_at}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 1
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_2
        )

    def test_get_task_paginated_via_duration(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
        test_task_2: TaskModel,
        test_task_3: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/paginated?duration=30")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data["total"] == 2
        assert TaskSchema.model_validate(data["items"][0]) == TaskSchema.model_validate(
            test_task_1
        )
        assert TaskSchema.model_validate(data["items"][1]) == TaskSchema.model_validate(
            test_task_3
        )

    def test_get_task_paginated_min_retries_too_small(self, test_client_v1: TestClient):
        result = test_client_v1.get("/tasks/paginated?min_retries=-1")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Minimum retries must be a positive number"

    def test_get_task_paginated_retry_range_backwards(self, test_client_v1: TestClient):
        result = test_client_v1.get("/tasks/paginated?min_retries=5&max_retries=1")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Minimum retries is larger than maximum retries"

    def test_get_task_paginated_duration_too_small(self, test_client_v1: TestClient):
        result = test_client_v1.get("/tasks/paginated?duration=-1")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Task duration must be a positive number"

    def test_get_task_paginated_started_ended_range_backwards(
        self, test_client_v1: TestClient
    ):
        result = test_client_v1.get(
            f"/tasks/paginated?started_at={datetime.now() + timedelta(minutes=6)}&ended_at={datetime.now()}"
        )
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Started at time is larger than ended at time"

    def test_get_task(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/{test_task_1.task_id}")
        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert TaskSchema.model_validate(data)
        assert TaskSchema.model_validate(data) == TaskSchema.model_validate(test_task_1)

    def test_get_task_not_exist(
        self,
        test_client_v1: TestClient,
        test_task_1: TaskModel,
    ):
        result = test_client_v1.get(f"/tasks/{test_task_1.id}")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Task does not exist"

    def test_get_task_status(self, test_client_v1: TestClient, test_task_2: TaskModel):
        mock_task = MagicMock()
        mock_task.state = "SUCCESS"
        mock_task.info = {"result": "done"}

        with patch("src.services.task.AsyncResult", return_value=mock_task):
            result = test_client_v1.get(f"/tasks/{test_task_2.task_id}/status")

        assert result.status_code == status.HTTP_200_OK

        data = result.json()
        assert data == {
            "status": "SUCCESS",
            "info": {"result": "done"},
        }

    def test_get_task_status_task_not_exist(
        self, test_client_v1: TestClient, test_task_2: TaskModel
    ):
        result = test_client_v1.get(f"/tasks/{test_task_2.id}/status")
        assert result.status_code == status.HTTP_404_NOT_FOUND

        data = result.json()
        assert data["detail"] == "Task does not exist"

    def test_get_task_status_is_pending(
        self, test_client_v1: TestClient, test_task_1: TaskModel
    ):
        result = test_client_v1.get(f"/tasks/{test_task_1.task_id}/status")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Task is waiting to be processed"

    def test_get_task_status_is_finished(
        self, test_client_v1: TestClient, test_task_3: TaskModel
    ):
        result = test_client_v1.get(f"/tasks/{test_task_3.task_id}/status")
        assert result.status_code == status.HTTP_400_BAD_REQUEST

        data = result.json()
        assert data["detail"] == "Task has finished processing"
