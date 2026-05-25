import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, or_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


if TYPE_CHECKING:
    from src.models import PersonalModel


class RankerModel(BaseModel):
    __tablename__ = "ranker"

    personal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("personal.id", ondelete="CASCADE"), nullable=False
    )
    day: Mapped[date] = mapped_column(Date, nullable=False)
    ranking: Mapped[Optional[int]] = mapped_column(Integer, default=None, nullable=True)

    text_events: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    text_notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    personal: Mapped["PersonalModel"] = relationship(back_populates="ranker")

    def __init__(self, personal_id: uuid.UUID, day: date, ranking: int | None = None):
        self.personal_id = personal_id
        self.day = day
        self.ranking = ranking

    @hybrid_property
    def contains_notes(self) -> bool:
        return self.text_events is not None or self.text_notes is not None

    @contains_notes.expression
    def contains_notes(cls):
        return or_(cls.text_events.isnot(None), cls.text_notes.isnot(None))  # type: ignore
