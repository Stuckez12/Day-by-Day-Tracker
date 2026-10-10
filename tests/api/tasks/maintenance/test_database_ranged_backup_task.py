import pytest


@pytest.mark.usefixtures("mock_task_db")
class TestDatabaseRangedBackupTask:
    def test_success(self, celery_worker: None):
        pass

    def test_workflow_failure(self, celery_worker: None):
        pass
