import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.core.password_hash import pwd_hash
from src.models import PersonnelModel
from src.schemas import (
    CreatePersonnelRequest,
    UpdatePersonnelDetailsRequest,
    UpdatePersonnelEmailRequest,
    UpdatePersonnelPasswordRequest,
)
from src.services.base import BaseDBService


class PersonnelService(BaseDBService[PersonnelModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=PersonnelModel)

    def get_by_email(self, email: str):
        return self.db.query(PersonnelModel).filter(PersonnelModel.email == email).one()

    def create_personnel(self, data: CreatePersonnelRequest) -> PersonnelModel:
        try:
            personnel = PersonnelModel(**data.model_dump())

        except TypeError:
            raise TypeError("Invalid data format provided for personnel")

        self.add(personnel)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def update_personnel_details(
        self, personnel: PersonnelModel, data: UpdatePersonnelDetailsRequest
    ) -> PersonnelModel:
        personnel = self.update_data_columns(personnel, data)
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def update_personnel_email(
        self, personnel: PersonnelModel, data: UpdatePersonnelEmailRequest
    ) -> PersonnelModel:
        personnel.email = data.email
        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def update_personnel_password(
        self, personnel: PersonnelModel, data: UpdatePersonnelPasswordRequest
    ) -> PersonnelModel:
        validated = pwd_hash.verify(data.current_password, personnel.password)

        if not validated:
            raise ValueError("Current password incorrect")

        try:
            personnel.password = pwd_hash.hash(data.new_password)

        except (TypeError, ValueError):
            raise ValueError("Unable to hash password. Please try again")

        self.db.commit()
        self.db.refresh(personnel)

        return personnel

    def personnel_exists(self, personnel_id: uuid.UUID) -> PersonnelModel:
        try:
            personnel = self.get_by_id(personnel_id)

        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personnel {personnel_id} not found",
            )

        return personnel
