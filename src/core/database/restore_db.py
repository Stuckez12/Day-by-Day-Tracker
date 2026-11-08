from src.schemas.application_settings import ApplicationSettingsSchema


def application_is_configured_to_be_restored(
    configurable_settings: ApplicationSettingsSchema,
) -> bool:
    return configurable_settings.RESTORE_DATABASE_TO_BACKUP_ID is not None
