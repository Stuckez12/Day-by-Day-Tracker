import os
import subprocess
from pathlib import Path

from src.schemas.application_settings import ApplicationSettingsSchema
from src.settings import app_config


def application_is_configured_to_be_restored(
    configurable_settings: ApplicationSettingsSchema,
) -> bool:
    return configurable_settings.RESTORE_DATABASE_TO_BACKUP_ID is not None


def restore_logical_backup_in_database(
    database_name: str, backup_file_path: Path
) -> None:
    command = [
        "pg_restore",
        "--clean",
        "--if-exists",
        "-h",
        app_config.DATABASE_HOST,
        "-p",
        str(app_config.DATABASE_PORT),
        "-U",
        app_config.DATABASE_USERNAME,
        "-d",
        database_name,
        backup_file_path,
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = app_config.DATABASE_PASSWORD

    try:
        subprocess.run(
            command,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        raise SystemError(f"""
Unable to restore database backup

RETURN CODE: {e.returncode}
STDOUT: {e.stdout}
STDERR: {e.stderr}
""")
