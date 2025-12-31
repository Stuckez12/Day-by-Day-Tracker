import uuid

from pydantic import BaseModel


class CreatePersonnelRequest(BaseModel):
    first_name: str
    last_name: str


class UpdatePersonnelRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class SelectPersonnelRequest(BaseModel):
    id: uuid.UUID
