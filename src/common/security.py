from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import NoResultFound

from src.common.dependencies import PersonnelServiceDep
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to find personnel. Please log in again",
        )

    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )


CurrentPersonnel = Annotated[PersonnelModel, Depends(get_current_personnel_id)]
