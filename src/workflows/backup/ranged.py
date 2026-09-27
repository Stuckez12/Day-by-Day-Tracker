from sqlalchemy.orm import Session

from src.core.s3_storage import ObjectStorage
from src.models import BackupModel
from src.workflows.backup.base import BaseBackupWorkflow


class RangedBackupWorkflow(BaseBackupWorkflow):
    def __init__(
        self,
        *,
        db: Session,
        backup_db: Session,
        backup_record: BackupModel,
        object_storage: ObjectStorage,
    ) -> None:
        super().__init__(
            db=db,
            backup_db=backup_db,
            backup_record=backup_record,
            object_storage=object_storage,
        )

    # ------------------------ DB Backup ----------------------- #

    # ----------------------- File Backup ---------------------- #

    # ------------------------ Metadata ------------------------ #
