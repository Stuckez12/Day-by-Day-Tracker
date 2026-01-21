import uuid

from datetime import date
from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from backend.models.base import BaseModel

if TYPE_CHECKING:
    from backend.models import PersonalModel


class RankerModel(BaseModel):
    __tablename__ = "ranker"

    personal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("personal.id"), nullable=False
    )
    day: Mapped[date] = mapped_column(Date, nullable=False)
    ranking: Mapped[Optional[int]] = mapped_column(Integer, default=None, nullable=True)

    personal: Mapped["PersonalModel"] = relationship(back_populates="ranker")

    def __init__(self, personal_id: uuid.UUID, day: date, ranking: int | None = None):
        self.personal_id = personal_id
        self.day = day
        self.ranking = ranking
