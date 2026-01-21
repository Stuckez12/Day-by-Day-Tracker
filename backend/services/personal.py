import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models import PersonalModel
from backend.schemas import CreatePersonnelRequest, UpdatePersonnelRequest
from backend.services.base import BaseDBService


class PersonalService(BaseDBService[PersonalModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=PersonalModel)

    def create_personnel(self, data: CreatePersonnelRequest) -> PersonalModel:
        try:
            personnel = PersonalModel(**data.model_dump())

        except TypeError:
            raise TypeError("Invalid data format provided for personnel")

        self.add(personnel)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def update_personnel(
        self, personnel: PersonalModel, data: UpdatePersonnelRequest
    ) -> PersonalModel:
        personnel = self.update_data_columns(personnel, data)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def delete_personnel(self, personnel: PersonalModel) -> None:
        self.delete(personnel)
        self.db.commit()

    def personnel_exists(self, personnel_id: uuid.UUID) -> PersonalModel:
        personnel = self.get_by_id(personnel_id)

        if personnel is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personnel {personnel_id} not found",
            )

        return personnel
