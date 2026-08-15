from enum import Enum


class BackupStatus(Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UPLOADED = "UPLOADED"
