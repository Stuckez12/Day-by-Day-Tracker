import uuid

from datetime import time
from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from backend.models.base import BaseModel

if TYPE_CHECKING:
    from backend.models import PersonalModel


class HabitsModel(BaseModel):
    __tablename__ = "habits"

    personal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("personal.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    occur: Mapped[str] = mapped_column(String, nullable=False)

    # How much you should achieve per timeline
    # e.g. achieve x habit 5 times per week
    achieve_units: Mapped[int] = mapped_column(Integer, nullable=False)
    achieve_timeline: Mapped[str] = mapped_column(String, nullable=False)
    achieve_type: Mapped[str] = mapped_column(String, nullable=False)

    notify_time: Mapped[time] = mapped_column(Time, nullable=False)

    personal: Mapped["PersonalModel"] = relationship(back_populates="habits")
