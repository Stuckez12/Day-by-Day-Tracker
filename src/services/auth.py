from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import PersonalModel
from src.schemas import CreatePersonnelRequest, LogInRequest
from src.services.personal import PersonalService


class AuthService(PersonalService):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db)

    def register(self, data: CreatePersonnelRequest) -> PersonalModel:
        exists = (
            self.db.query(PersonalModel)
            .filter(PersonalModel.email == data.email)
            .first()
        )

        if exists:
            raise ValueError("Email already in use")

        try:
            data.password = pwd_hash.hash(data.password)

        except (TypeError, ValueError):
            raise ValueError("Unable to hash password. Please try again")

        return self.create_personnel(data)

    def log_in(self, data: LogInRequest):
        pass
