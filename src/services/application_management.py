from sqlalchemy.orm import Session

from src.core.app_settings import (
    configure_application_settings,
    get_configurable_application_settings,
)
from src.exc import HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID
from src.models import BackupModel
from src.models.base import BaseModel
from src.schemas import ApplicationSettingsSchema
from src.services import BackupService
from src.services.base import BaseDBService

from .dependencies_value import validate_backup_service


class ApplicationManagementService(BaseDBService[BaseModel]):
    backup_service = validate_backup_service

    def __init__(self, db: Session, backup_service: BackupService) -> None:
        super().__init__(db=db, model=BaseModel)

        self._backup_service = backup_service

    @property
    def app_settings(self) -> ApplicationSettingsSchema:
        return get_configurable_application_settings()

    def get_what_backup_app_will_be_restored_to(self) -> BackupModel:
        restore_backup_id = self.app_settings.RESTORE_DATABASE_TO_BACKUP_ID

        if restore_backup_id is None:
            raise HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID

        return self.backup_service.get_by_backup_id(restore_backup_id)

    def specify_backup_app_will_be_restored_to(self, backup: BackupModel) -> None:
        config_app_settings = self.app_settings
        config_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = backup.id

        configure_application_settings(config_app_settings)

    def set_app_will_be_restored_to_no_backup(self) -> None:
        config_app_settings = self.app_settings
        config_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = None

        configure_application_settings(config_app_settings)
