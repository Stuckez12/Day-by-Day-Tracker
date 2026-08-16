import subprocess
from pathlib import Path

import pytest
from celery.result import AsyncResult
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.enums import BackupStatus
from src.models import BackupModel, MetaModel
from src.schemas import BackupSchema
from src.tasks import verify_backup


@pytest.mark.usefixtures("mock_task_db")
class TestVerifyBackupTask:
    def test_success(
        self,
        shared_tmp_path: Path,
        mocker: MockerFixture,
        celery_worker: None,
        test_backup_session: Session,
        test_backup_zip: str,
        test_metadata: MetaModel,
        test_backup: BackupModel,
    ):
        mocker.patch("src.routes.backup.app_config.BACKUP_PATH", str(shared_tmp_path))
        mocker.patch.object(subprocess, "run", return_value=None)

        test_metadata.zip_filename = test_backup_zip
        test_backup_session.commit()

        task: AsyncResult = verify_backup.delay(backup_id=test_backup.id)
        backup = BackupSchema.model_validate(task.result)
        assert backup.status == BackupStatus.SUCCESS, backup.model_dump()
        assert backup.error_message is None
        assert backup.error_traceback is None
