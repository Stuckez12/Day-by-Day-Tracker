from enum import Enum


class BackupType(Enum):
    RANGED = "RANGED"
    LOGICAL = "LOGICAL"
    UPLOADED = "UPLOADED"
