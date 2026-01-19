import uuid

from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self, clean: bool = False):
        if clean:
            # Return a purely clean dictionary by converting non string params into string
            result = {}

            for c in self.__table__.columns:
                value = getattr(self, c.name)

                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%dT%H:%M:%S.%f")

                if isinstance(value, uuid.UUID):
                    value = str(value)

                result[c.name] = value

            return result

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"  # pragma: no cover
