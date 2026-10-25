from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.services import BackupService


def _validate_service(obj, service_name: str, private_attribute_name: str):
    if not hasattr(obj, private_attribute_name):
        raise RuntimeError(
            f"This service does not define self.{private_attribute_name} in the init"
        )

    value = getattr(obj, private_attribute_name)

    if value is None:
        raise RuntimeError(f"{service_name} was not provided")

    return value


@property
def validate_backup_service(self) -> BackupService:
    return _validate_service(self, "BackupService", "_backup_service")
