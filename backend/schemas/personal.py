import uuid

from pydantic import BaseModel, ValidationInfo, field_validator


def validate_name(value: str, column: str):
    if len(value) <= 0:
        raise ValueError(f"{column} must not be empty")

    return value


class PersonnelSchema(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str | None, info: ValidationInfo) -> str:
        if len(value) <= 0:
            raise ValueError(f"{info.field_name} must not be empty")

        return value


class CreatePersonnelRequest(PersonnelSchema): ...


class UpdatePersonnelRequest(PersonnelSchema):
    first_name: str | None = None
    last_name: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str | None, info: ValidationInfo) -> str:
        if value is None:
            return value

        if len(value) <= 0:
            raise ValueError(f"{info.field_name} must not be empty")

        return value


class SelectPersonnelRequest(BaseModel):
    id: uuid.UUID
