import uuid

import pytest
from sqlalchemy.exc import NoResultFound

from src.models import BackupModel
from src.services import BackupService


class TestGetBackupByIDService:
    def test_success(
        self, test_backup_service: BackupService, test_backup: BackupModel
    ):
        backup = test_backup_service.get_by_backup_id(test_backup.id)
        assert backup == test_backup

    def test_not_found(self, test_backup_service: BackupService):
        with pytest.raises(NoResultFound):
            test_backup_service.get_by_backup_id(uuid.uuid4())


class TestGetBackupByTaskIDService:
    def test_success(
        self, test_backup_service: BackupService, test_backup: BackupModel
    ):
        backup = test_backup_service.get_by_task_id(test_backup.celery_id)
        assert backup == test_backup

    def test_not_found(self, test_backup_service: BackupService):
        with pytest.raises(NoResultFound):
            test_backup_service.get_by_task_id(uuid.uuid4())


class TestGetAllBackupsService:
    def test_success(
        self,
        test_backup_service: BackupService,
        test_backup: BackupModel,
        test_backup_2: BackupModel,
    ):
        backups = test_backup_service.get_all()
        assert len(backups) == 2
        assert [type(backup) == BackupModel for backup in backups]
