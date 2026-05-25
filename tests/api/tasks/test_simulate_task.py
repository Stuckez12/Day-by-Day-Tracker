import time

from celery.result import AsyncResult
from pytest_mock import MockerFixture

from src.tasks import simulate_celery_task


class TestSimulateTask:
    def test_simulate(self, mocker: MockerFixture, celery_worker: None):
        mocker.patch.object(time, "sleep", return_value=None)
        task: AsyncResult = simulate_celery_task.delay()
        assert task.result["progress"] == 100
