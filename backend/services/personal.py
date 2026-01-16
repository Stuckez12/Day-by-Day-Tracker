import uuid

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from backend.models import PersonalModel
from backend.schemas import CreatePersonnelRequest, UpdatePersonnelRequest
from backend.services.base import BaseDBService


class PersonalService(BaseDBService[PersonalModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=PersonalModel)

    def create_personnel(self, data: CreatePersonnelRequest) -> PersonalModel:
        personnel = PersonalModel(**data.model_dump())

        self.add(personnel)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def update_personnel(
        self, personnel_id: str, data: UpdatePersonnelRequest
    ) -> PersonalModel:
        personnel = self.get_by_id(personnel_id)

        self.update_data_columns(personnel, data)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def delete_personnel(self, id: uuid.UUID) -> PersonalModel:
        personnel = self.get_by_id(id)
        self.delete(personnel)
        self.db.commit()

        return personnel
