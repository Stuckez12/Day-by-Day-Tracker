from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import Generic, Self, Type, TypeVar
from uuid import UUID

from backend.models.base import Base, BaseModel


Model = TypeVar("Model", bound=BaseModel)
ModelRow = TypeVar("ModelRow", bound=Base)


class BaseDBService(Generic[Model]):
    model: type[Model]

    def __init__(self: Self, db: Session):
        self.db: Session = db

    def get_by_id(self: Self, id: UUID):
        try:
            return (
                self.db.query(self.__class__.model)
                .filter(self.__class__.model.id == id)
                .first()
            )

        except NoResultFound:
            raise ValueError("ID not within database")

    def get_paginated(self: Self, page: int, page_size: int):
        offset = (page - 1) * page_size
        return self.db.query(self.__class__.model).limit(page_size).offset(offset)

    def get_all(self: Self):
        return self.db.query(self.__class__.model).all()

    def add(self: Self, row: ModelRow):
        self.db.add(row)
        self.db.flush()

    def add_all(self: Self, rows: list[ModelRow]):
        self.db.add_all(rows)
        self.db.flush()

    def update_data_columns(self: Self, row: ModelRow, data: Type[BaseModel]):
        for key, value in data.model_dump(exclude="id", exclude_none=True).items():
            setattr(row, key, value)

    def delete(self: Self, row: ModelRow):
        self.db.delete(row)

    def bulk_delete(self: Self, rows: list[ModelRow]):
        for row in rows:
            self.delete(row)
