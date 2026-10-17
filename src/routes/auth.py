from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter

from src.common.dependencies import AuthServiceDep
from src.common.security import create_access_token
from src.core import client_ipaddress
from src.schemas import CreatePersonnelRequest, LogInRequest, SlimPersonnelSchema
from src.settings import app_config


limiter = Limiter(key_func=client_ipaddress, enabled=app_config.APP_ENV != "test")
api = APIRouter(prefix="/auth", tags=["Auth"])


@api.post(
    "/register", response_model=SlimPersonnelSchema, status_code=status.HTTP_201_CREATED
)
@limiter.limit("8/30seconds")
def register_personnel(
    request: Request,  # Required for limiter
    data: CreatePersonnelRequest,
    service: AuthServiceDep,
):
    return service.register(data)


@api.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("8/30seconds")
def log_in(
    request: Request,  # Required for limiter
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
):
    personnel = service.log_in(
        LogInRequest(email=form_data.username, password=form_data.password)
    )

    return {
        "access_token": create_access_token(personnel.id),
        "token_type": "bearer",
        "personnel": SlimPersonnelSchema.model_validate(personnel).model_dump(),
    }
