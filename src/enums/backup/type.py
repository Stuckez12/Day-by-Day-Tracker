from enum import Enum


class BackupType(Enum):
    RANGED_DAY = "RANGED_DAY"
    RANGED_WEEK = "RANGED_WEEK"
    LOGICAL = "LOGICAL"
    UPLOADED = "UPLOADED"
