from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.exc import (
    HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID,
    HTTP_EXC_BACKUP_NOT_FOUND,
    HTTP_EXC_NOT_AN_ADMIN,
)
from src.models import BackupModel
from src.schemas import ApplicationSettingsSchema, BackupSchema
from src.services import application_management


class TestGetRestoreBackupRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        test_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = test_backup.id
        mocker.patch.object(
            application_management,
            "get_configurable_application_settings",
            return_value=test_app_settings,
        )

        result = test_client_admin_session.get(
            "/app-management/backup/restore-to-backup"
        )

        assert result.status_code == status.HTTP_200_OK
        assert BackupSchema.model_validate(
            result.json()
        ) == BackupSchema.model_validate(test_backup)

    def test_unauthenticated_restricted(self, test_app: TestClient):
        result = test_app.get("/app-management/backup/restore-to-backup")

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {"detail": "Not authenticated"}

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.get(
            "/app-management/backup/restore-to-backup"
        )

        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code
        assert result.json() == {"detail": HTTP_EXC_NOT_AN_ADMIN.detail}

    def test_no_restore_backup_configured(
        self,
        test_client_admin_session: TestClient,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        test_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = None
        mocker.patch.object(
            application_management,
            "get_configurable_application_settings",
            return_value=test_app_settings,
        )

        result = test_client_admin_session.get(
            "/app-management/backup/restore-to-backup"
        )

        assert (
            result.status_code == HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID.status_code
        )
        assert result.json() == {
            "detail": HTTP_EXC_APP_SETTINGS_NO_RESTORE_BACKUP_ID.detail
        }

    def test_backup_not_found(
        self,
        test_client_admin_session: TestClient,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        mocker.patch.object(
            application_management,
            "get_configurable_application_settings",
            return_value=test_app_settings,
        )

        result = test_client_admin_session.get(
            "/app-management/backup/restore-to-backup"
        )

        assert result.status_code == HTTP_EXC_BACKUP_NOT_FOUND.status_code
        assert result.json() == {"detail": HTTP_EXC_BACKUP_NOT_FOUND.detail}


class TestSetRestoreBackupRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_backup: BackupModel,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        expected_settings = test_app_settings.model_copy(
            update={"RESTORE_DATABASE_TO_BACKUP_ID": test_backup.id}
        )
        mocker.patch.object(
            application_management,
            "get_configurable_application_settings",
            return_value=test_app_settings,
        )
        configure_settings = mocker.patch.object(
            application_management, "configure_application_settings"
        )

        result = test_client_admin_session.post(
            f"/app-management/backup/restore-to-backup/{test_backup.id}"
        )

        assert result.status_code == status.HTTP_202_ACCEPTED
        assert result.json() == {
            "detail": "Backup successfully established as the restore point"
        }
        configure_settings.assert_called_once_with(expected_settings)

    def test_unauthenticated_restricted(self, test_app: TestClient):
        result = test_app.post(f"/app-management/backup/restore-to-backup/{uuid4()}")

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {"detail": "Not authenticated"}

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.post(
            f"/app-management/backup/restore-to-backup/{uuid4()}"
        )

        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code
        assert result.json() == {"detail": HTTP_EXC_NOT_AN_ADMIN.detail}

    def test_invalid_backup_id(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.post(
            "/app-management/backup/restore-to-backup/invalid"
        )

        assert result.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert result.json()["detail"][0]["loc"] == ["path", "backup_id"]

    def test_backup_not_found(self, test_client_admin_session: TestClient):
        result = test_client_admin_session.post(
            f"/app-management/backup/restore-to-backup/{uuid4()}"
        )

        assert result.status_code == HTTP_EXC_BACKUP_NOT_FOUND.status_code
        assert result.json() == {"detail": HTTP_EXC_BACKUP_NOT_FOUND.detail}


class TestUnsetRestoreBackupRoute:
    def test_success(
        self,
        test_client_admin_session: TestClient,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        expected_settings = test_app_settings.model_copy(
            update={"RESTORE_DATABASE_TO_BACKUP_ID": None}
        )
        mocker.patch.object(
            application_management,
            "get_configurable_application_settings",
            return_value=test_app_settings,
        )
        configure_settings = mocker.patch.object(
            application_management, "configure_application_settings"
        )

        result = test_client_admin_session.delete(
            "/app-management/backup/restore-to-backup"
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {
            "detail": "Backup successfully removed as the restore point"
        }
        configure_settings.assert_called_once_with(expected_settings)

    def test_success_when_no_restore_backup_configured(
        self,
        test_client_admin_session: TestClient,
        test_app_settings: ApplicationSettingsSchema,
        mocker: MockerFixture,
    ):
        test_app_settings.RESTORE_DATABASE_TO_BACKUP_ID = None
        expected_settings = test_app_settings.model_copy()
        mocker.patch.object(
            application_management,
            "get_configurable_application_settings",
            return_value=test_app_settings,
        )
        configure_settings = mocker.patch.object(
            application_management, "configure_application_settings"
        )

        result = test_client_admin_session.delete(
            "/app-management/backup/restore-to-backup"
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json() == {
            "detail": "Backup successfully removed as the restore point"
        }
        configure_settings.assert_called_once_with(expected_settings)

    def test_unauthenticated_restricted(self, test_app: TestClient):
        result = test_app.delete("/app-management/backup/restore-to-backup")

        assert result.status_code == status.HTTP_401_UNAUTHORIZED
        assert result.json() == {"detail": "Not authenticated"}

    def test_non_admin_restricted(self, test_client_user_session: TestClient):
        result = test_client_user_session.delete(
            "/app-management/backup/restore-to-backup"
        )

        assert result.status_code == HTTP_EXC_NOT_AN_ADMIN.status_code
        assert result.json() == {"detail": HTTP_EXC_NOT_AN_ADMIN.detail}
