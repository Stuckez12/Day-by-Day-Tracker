import uuid

import logging

from pydantic import BaseModel, ValidationInfo, field_validator, Field


class PersonnelSchema(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str, info: ValidationInfo) -> str:
        if len(value) <= 0:
            raise ValueError(f"{info.field_name} must not be empty")

        return value


class CreatePersonnelRequest(PersonnelSchema): ...


class UpdatePersonnelRequest(PersonnelSchema):
    first_name: str | None = None
    last_name: str | None = None


class SelectPersonnelRequest(BaseModel):
    id: uuid.UUID
