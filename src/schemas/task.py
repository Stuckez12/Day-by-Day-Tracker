import uuid

from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, model_validator

from src.enums import TaskStatus


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: uuid.UUID
    name: str
    status: TaskStatus
    retries: int

    started_at: datetime | None = None
    ended_at: datetime | None = None

    error: str | None = None


class TaskPaginated(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str | None = None
    name: str | None = None
    task_status: list[TaskStatus] | None = None
    min_retries: int | None = None
    max_retries: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration: int | None = None

    @model_validator(mode="after")
    def validate_rank(self):
        if self.min_retries is not None:
            if self.min_retries < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Minimum retries must be a positive number",
                )

        if self.min_retries is not None and self.max_retries is not None:
            if self.min_retries > self.max_retries:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Minimum retries is largewr than maximum retries",
                )

        if self.duration is not None:
            if self.duration < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task duration must be a positive number",
                )

        if self.started_at is not None and self.ended_at is not None:
            if self.started_at > self.ended_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Minimum retries is largewr than maximum retries",
                )

        return self
