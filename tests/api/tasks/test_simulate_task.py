from celery.result import AsyncResult

from src.tasks import simulate_celery_task


class TestSimulateTask:
    def test_simulate(self, celery_worker):
        task: AsyncResult = simulate_celery_task.delay()
        assert task.result["progress"] == 100
