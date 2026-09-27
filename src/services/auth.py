import logging

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.core.password_hash import pwd_hash
from src.models import PersonnelModel
from src.schemas import CreatePersonnelRequest, LogInRequest
from src.services.personnel import PersonnelService
from src.settings import app_config


class AuthService(PersonnelService):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db)

    def register(self, data: CreatePersonnelRequest) -> PersonnelModel:
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

    def log_in(self, data: LogInRequest) -> PersonnelModel:
        try:
            personnel = (
                self.db.query(PersonnelModel)
                .filter(PersonnelModel.email == data.email)
                .one()
            )

        except NoResultFound:
            raise ValueError("Invalid email or password")

        confirm_password = pwd_hash.verify(data.password, personnel.password)

        if not confirm_password:
            raise ValueError("Invalid email or password")

        return personnel

    def seed_user(self) -> None:
        try:
            seed_data = CreatePersonnelRequest(
                email=app_config.USER_EMAIL,
                password=app_config.USER_PASSWORD,
                first_name=app_config.USER_FIRST_NAME,
                last_name=app_config.USER_LAST_NAME,
            )

            logging.info("Attempting To Seed User")
            self.register(seed_data)

        except Exception:
            logging.warning("Seeding user data is invalid. Cancelled seeding")
