from enum import Enum


class TaskScheduleStatus(Enum):
    QUEUED = "QUEUED"
    PUBLISHED = "PUBLISHED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
