from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


if TYPE_CHECKING:
    from src.models import RankerModel


class PersonnelModel(BaseModel):
    __tablename__ = "personal"

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    ranker: Mapped["RankerModel"] = relationship(
        back_populates="personnel", cascade="all, delete-orphan"
    )

    def __init__(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
