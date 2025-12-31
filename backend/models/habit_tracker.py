import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import BaseModel


class HabitTrackerModel(BaseModel):
    __tablename__ = "habit_tracker"

    type: Mapped[str] = mapped_column(String, default="ranking", nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=None, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    text: Mapped[str] = mapped_column(String, default=None, nullable=True)

    habit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("habits.id"), nullable=False)
