import uuid

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.models import PersonalModel
from backend.schemas import CreatePersonnelRequest, UpdatePersonnelRequest
from backend.services.base import BaseDBService


class PersonalService(BaseDBService[PersonalModel]):
    model = PersonalModel

    def __init__(self, db: Session):
        super().__init__(db)

    def create_personnel(self, data: CreatePersonnelRequest):
        row = PersonalModel(**data.model_dump())

        self.add(row)
        self.db.commit()
        self.db.refresh(row)

        return row

    def update_personnel(self, personnel_id: str, data: UpdatePersonnelRequest):
        personnel = self.get_by_id(personnel_id)

        self.update_data_columns(personnel, data)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def delete_personnel(self, id: uuid.UUID):
        personnel = self.get_by_id(id)
        self.delete(personnel)
        self.db.commit()

        return personnel
