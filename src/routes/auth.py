from fastapi import APIRouter, status

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
def log_in(request: LogInRequest, service: AuthServiceDep):
    personnel = service.log_in(request)

    return {
        "access_token": create_access_token(personnel.id),
        "token_type": "bearer",
        "personnel": personnel.model_dump(),
    }


@api.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def log_out():
    return None
