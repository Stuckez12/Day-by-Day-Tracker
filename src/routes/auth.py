import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.common import AuthServiceDep
from src.common.security import create_access_token
from src.schemas import CreatePersonnelRequest, LogInRequest, SlimPersonnelSchema


api = APIRouter(prefix="/auth", tags=["Auth"])


@api.post(
    "/register", response_model=SlimPersonnelSchema, status_code=status.HTTP_201_CREATED
)
def register_personnel(request: CreatePersonnelRequest, service: AuthServiceDep):
    return service.register(request)


@api.post("/login", status_code=status.HTTP_200_OK)
def log_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep
):
    logging.info("Entered Route")
    logging.info(form_data.password)
    personnel = service.log_in(
        LogInRequest(email=form_data.username, password=form_data.password)
    )

    return {
        "access_token": create_access_token(personnel.id),
        "token_type": "bearer",
        "personnel": SlimPersonnelSchema.model_validate(personnel).model_dump(),
    }
