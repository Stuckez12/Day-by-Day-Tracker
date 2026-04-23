import uuid

from pydantic import BaseModel, ValidationInfo, field_validator


class PersonnelSchema(BaseModel):
    email: str

    first_name: str
    last_name: str

    @field_validator("email", "first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str, info: ValidationInfo) -> str:
        if len(value) <= 0:
            raise ValueError(f"{info.field_name} must not be empty")

        return value


class CreatePersonnelRequest(PersonnelSchema):
    password: str

    @field_validator("password")
    @classmethod
    def validate_name(cls, value: str, info: ValidationInfo) -> str:
        if len(value) <= 0:
            raise ValueError(f"{info.field_name} must not be empty")

        return value


class UpdatePersonnelRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str, info: ValidationInfo) -> str:
        if len(value) <= 0:
            raise ValueError(f"{info.field_name} must not be empty")

        return value


class SelectPersonnelRequest(BaseModel):
    id: uuid.UUID
