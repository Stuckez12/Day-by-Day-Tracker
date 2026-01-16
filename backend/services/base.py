from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Generic, Self, Type, TypeVar
from uuid import UUID

from backend.models.base import Base, BaseModel


Model = TypeVar("Model", bound=Base)


class BaseDBService(Generic[Model]):
    def __init__(self: Self, db: Session, model: type[Model]) -> None:
        self.db: Session = db
        self.model = model

    def get_by_id(self: Self, id: UUID) -> Model | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_paginated(self: Self, page: int, page_size: int) -> list[Model]:
        offset = (page - 1) * page_size
        return self.db.query(self.model).limit(page_size).offset(offset)

    def get_all(self: Self) -> list[Model]:
        return self.db.query(self.model).all()

    def add(self: Self, row: Model) -> None:
        self.db.add(row)
        self.db.flush()

    def add_all(self: Self, rows: list[Model]) -> None:
        self.db.add_all(rows)
        self.db.flush()

    def update_data_columns(self: Self, row: Model, data: Type[BaseModel]) -> None:
        for key, value in data.model_dump(exclude="id", exclude_none=True).items():
            setattr(row, key, value)

    def delete(self: Self, row: Model) -> None:
        self.db.delete(row)
        self.db.flush()

    def bulk_delete(self: Self, rows: list[Model]) -> None:
        for row in rows:
            self.delete(row)

        self.db.flush()
