import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


if TYPE_CHECKING:
    from src.models import PersonnelModel


class RankerModel(BaseModel):
    __tablename__ = "ranker"

    personnel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("personal.id", ondelete="CASCADE"), nullable=False
    )
    day: Mapped[date] = mapped_column(Date, nullable=False)
    ranking: Mapped[Optional[int]] = mapped_column(Integer, default=None, nullable=True)

    text_events: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    text_notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    personnel: Mapped["PersonnelModel"] = relationship(back_populates="ranker")

    def __init__(self, personnel_id: uuid.UUID, day: date, ranking: int | None = None):
        self.personnel_id = personnel_id
        self.day = day
        self.ranking = ranking
