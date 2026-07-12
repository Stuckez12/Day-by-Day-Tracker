from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from src.settings import app_config


bearer_scheme = HTTPBearer()


def create_access_token(personnel_id: UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=app_config.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(personnel_id), "exp": expires_at}

    return jwt.encode(payload, app_config.JWT_SECRET, algorithm="HS256")


def get_current_personnel_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UUID:
    try:
        payload = jwt.decode(
            credentials.credentials,
            app_config.JWT_SECRET,
            algorithms=["HS256"],
        )
        return UUID(payload["sub"])

    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )


CurrentPersonnelID = Annotated[UUID, Depends(get_current_personnel_id)]
