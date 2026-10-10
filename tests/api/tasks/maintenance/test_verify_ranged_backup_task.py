import pytest
from pytest_mock import MockerFixture


@pytest.mark.usefixtures("mock_task_db")
class TestVerifyRangedBackupTask:
    def test_success(
        self,
        mocker: MockerFixture,
        celery_worker: None,
    ):
        pass

    def test_no_backup_record(self, celery_worker: None):
        pass

    def test_backup_type_is_invalid(self, celery_worker: None):
        pass

    def test_backup_has_no_metadata(self, celery_worker: None):
        pass

    def test_workflow_failure(self, celery_worker: None):
        pass
