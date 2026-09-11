from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import NoResultFound

from src.common.dependencies import PersonnelServiceDep
from src.exc import HTTP_EXC_INVALID_TOKEN, HTTP_EXC_PERSONNEL_DOES_NOT_EXIST
from src.models.personnel import PersonnelModel
from src.settings import app_config


bearer_scheme = HTTPBearer()


def create_access_token(personnel_id: UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=app_config.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(personnel_id), "exp": expires_at}

    return jwt.encode(payload, app_config.JWT_SECRET, algorithm="HS256")


def get_current_personnel_id(
    personnel_service: PersonnelServiceDep,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> PersonnelModel:
    try:
        payload = jwt.decode(
            credentials.credentials,
            app_config.JWT_SECRET,
            algorithms=["HS256"],
        )
        personnel_id = payload["sub"]

        return personnel_service.get_by_id(personnel_id)

    except NoResultFound:
        raise HTTP_EXC_PERSONNEL_DOES_NOT_EXIST

    except (InvalidTokenError, KeyError, ValueError):
        raise HTTP_EXC_INVALID_TOKEN


CurrentPersonnel = Annotated[PersonnelModel, Depends(get_current_personnel_id)]
