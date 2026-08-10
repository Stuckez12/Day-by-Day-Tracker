from enum import Enum


class BackupType(Enum):
    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    DIFFERENTIAL = "DIFFERENTIAL"
    LOGICAL = "LOGICAL"
