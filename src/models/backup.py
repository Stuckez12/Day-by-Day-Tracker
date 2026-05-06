from datetime import datetime
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class BackupModel(BaseModel):
    __tablename__ = "backups"

    name: Mapped[str] = mapped_column(String, nullable=False)
    backup_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
