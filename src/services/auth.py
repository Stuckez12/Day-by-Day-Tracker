from fastapi import Response
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.common.password_hash import pwd_hash
from src.models import PersonalModel
from src.schemas import CreatePersonnelRequest, LogInRequest
from src.services.personal import PersonalService


class AuthService(PersonalService):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db)

    def register(self, data: CreatePersonnelRequest) -> PersonalModel:
        try:
            self.get_by_email(data.email)

            raise ValueError("Email already in use")

        except NoResultFound:
            pass

        try:
            data.password = pwd_hash.hash(data.password)

        except (TypeError, ValueError):
            raise ValueError("Unable to hash password. Please try again")

        return self.create_personnel(data)

    def log_in(self, data: LogInRequest) -> PersonalModel:
        try:
            personnel = (
                self.db.query(PersonalModel)
                .filter(PersonalModel.email == data.email)
                .one()
            )

        except NoResultFound:
            raise ValueError("Invalid email or password")

        confirm_password = pwd_hash.verify(data.password, personnel.password)

        if not confirm_password:
            raise ValueError("Invalid email or password")

        return personnel

    def set_login_cookies(
        self, response: Response, personnel: PersonalModel
    ) -> Response:
        response.set_cookie(
            "personnel_id",
            str(personnel.id),
            httponly=True,
            path="/",
            samesite="lax",
        )

        return response
