from pydantic import BaseModel


class LogInRequest(BaseModel):
    email: str
    password: str
