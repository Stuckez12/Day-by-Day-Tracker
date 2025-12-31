from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from backend.models.base import BaseModel

if TYPE_CHECKING:
    from backend.models import HabitsModel, RankerModel


class PersonalModel(BaseModel):
    __tablename__ = "personal"

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    habits: Mapped["HabitsModel"] = relationship(back_populates="personal")
    ranker: Mapped["RankerModel"] = relationship(back_populates="personal")

    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name
