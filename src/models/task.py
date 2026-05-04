import uuid

from datetime import datetime, time
from sqlalchemy import DateTime, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.enums import TaskStatus
from src.models.base import BaseModel


class TaskModel(BaseModel):
    __tablename__ = "tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(String, nullable=False)
    retries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    task_duration: Mapped[time] = mapped_column(Time, nullable=True)

    error: Mapped[str] = mapped_column(String, nullable=True)

    def __init__(self, task_id: uuid.UUID, name: str, status: TaskStatus):
        self.task_id = task_id
        self.name = name
        self.status = status.value
