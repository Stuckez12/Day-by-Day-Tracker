import pytest

from fastapi import status
from fastapi.testclient import TestClient

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

        assert False

        # started_at
        # ended_at
        # duration
        {
            "items": [
                {
                    "task_id": "26972faf-938c-47b2-a232-e96e5188bd32",
                    "name": "task1",
                    "status": "PENDING",
                    "retries": 0,
                    "started_at": "2026-05-10T21:58:47.169036",
                    "ended_at": "2026-05-10T21:59:47.169042",
                    "error": "error message",
                }
            ],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }
