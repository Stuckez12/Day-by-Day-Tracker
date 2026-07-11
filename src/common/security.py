import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from src.settings import app_config


bearer_scheme = HTTPBearer()


def _jwt_secret() -> str:
    # The fallback prevents existing local environments from breaking while a
    # dedicated JWT_SECRET is introduced. Production should set JWT_SECRET.
    secret = app_config.JWT_SECRET or app_config.NEXTAUTH_SECRET
    if not secret:
        raise RuntimeError("JWT_SECRET must be configured")

    return secret


def create_access_token(personnel_id: uuid.UUID) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=app_config.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(personnel_id), "exp": expires_at}

    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def get_current_personnel_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> uuid.UUID:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _jwt_secret(),
            algorithms=["HS256"],
        )
        return uuid.UUID(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise unauthorized from None
