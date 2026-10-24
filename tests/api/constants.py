from pydantic import BaseModel


class InvalidSchema(BaseModel):
    field_1: str = "field"
    field_2: int = 500
    field_3: list[str] = ["field", "field", "field"]


INVALID_PERSONNEL_ID = "12345678-1234-5678-1234-567812345678"

VALID_PASSWORD = "Password1."
INVALID_PASSWORD = "Invalid1."
