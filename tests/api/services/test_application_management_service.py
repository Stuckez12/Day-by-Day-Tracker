import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture, MockType
from sqlalchemy.exc import NoResultFound

from src.exc import HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID
from src.models import BackupModel
from src.schemas import ApplicationSettingsSchema
from src.services import ApplicationManagementService


@pytest.fixture
def mock_app_settings(
    mocker: MockerFixture, test_app_settings: ApplicationSettingsSchema
):
    mocker.patch(
        "src.services.application_management.get_configurable_application_settings",
        return_value=test_app_settings,
    )
    return test_app_settings


@pytest.fixture
def configure_settings(mocker: MockerFixture):
    return mocker.patch(
        "src.services.application_management.configure_application_settings"
    )


class TestApplicationSettingsProperty:
    def test_reads_current_settings_on_each_access(
        self,
        test_application_management_service: ApplicationManagementService,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        current_settings = ApplicationSettingsSchema()
        mocker.patch(
            "src.services.application_management.get_configurable_application_settings",
            side_effect=[test_app_settings, current_settings],
        )

        first = test_application_management_service.app_settings
        second = test_application_management_service.app_settings

        assert first == test_app_settings
        assert second == current_settings


class TestGetRestoreBackupService:
    def test_success(
        self,
        test_application_management_service: ApplicationManagementService,
        mock_app_settings: ApplicationSettingsSchema,
        test_backup: BackupModel,
    ):
        mock_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = test_backup.id

        backup = test_application_management_service.get_what_backup_app_will_be_restored_to()

        assert backup == test_backup

    def test_no_restore_backup_configured(
        self,
        test_application_management_service: ApplicationManagementService,
        mock_app_settings: ApplicationSettingsSchema,
    ):
        mock_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = None

        with pytest.raises(HTTPException) as exc:
            test_application_management_service.get_what_backup_app_will_be_restored_to()

        assert exc.value is HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID

    @pytest.mark.usefixtures("mock_app_settings")
    def test_backup_not_found(
        self, test_application_management_service: ApplicationManagementService
    ):
        with pytest.raises(NoResultFound):
            test_application_management_service.get_what_backup_app_will_be_restored_to()


class TestSpecifyRestoreBackupService:
    def test_success_preserves_other_settings(
        self,
        test_application_management_service: ApplicationManagementService,
        mock_app_settings: ApplicationSettingsSchema,
        test_backup: BackupModel,
        configure_settings: MockType,
    ):
        mock_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = None

        test_application_management_service.specify_backup_app_will_be_restored_to(
            test_backup
        )

        configure_settings.assert_called_once_with(
            ApplicationSettingsSchema(
                RESTORE_DATABASE_TO_BACKUP_ID=test_backup.id,
                CANCEL_CURRENT_RESTORE_DATABASE_TASK=True,
            )
        )

    @pytest.mark.usefixtures("mock_app_settings")
    def test_replaces_existing_restore_backup(
        self,
        test_application_management_service: ApplicationManagementService,
        test_backup: BackupModel,
        configure_settings: MockType,
    ):
        test_application_management_service.specify_backup_app_will_be_restored_to(
            test_backup
        )

        configure_settings.assert_called_once_with(
            ApplicationSettingsSchema(
                RESTORE_DATABASE_TO_BACKUP_ID=test_backup.id,
                CANCEL_CURRENT_RESTORE_DATABASE_TASK=True,
            )
        )


class TestUnsetRestoreBackupService:
    @pytest.mark.usefixtures("mock_app_settings")
    def test_success_preserves_other_settings(
        self,
        test_application_management_service: ApplicationManagementService,
        configure_settings: MockType,
    ):
        test_application_management_service.set_app_will_be_restored_to_no_backup()

        configure_settings.assert_called_once_with(
            ApplicationSettingsSchema(CANCEL_CURRENT_RESTORE_DATABASE_TASK=True)
        )

    def test_success_when_no_restore_backup_configured(
        self,
        test_application_management_service: ApplicationManagementService,
        mock_app_settings: ApplicationSettingsSchema,
        configure_settings: MockType,
    ):
        mock_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = None

        test_application_management_service.set_app_will_be_restored_to_no_backup()

        configure_settings.assert_called_once_with(
            ApplicationSettingsSchema(CANCEL_CURRENT_RESTORE_DATABASE_TASK=True)
        )
