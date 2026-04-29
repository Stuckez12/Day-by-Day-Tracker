import uuid

from fastapi import APIRouter, Request, Response, status

from src.common import AuthServiceDep
from src.schemas import CreatePersonnelRequest, LogInRequest, PersonnelSchema


api = APIRouter(prefix="/auth", tags=["Auth"])


@api.post(
    "/register", response_model=PersonnelSchema, status_code=status.HTTP_201_CREATED
)
def register_personnel(request: CreatePersonnelRequest, service: AuthServiceDep):
    return service.register(request)


@api.post("/login", status_code=status.HTTP_200_OK)
def log_in(request: LogInRequest, response: Response, service: AuthServiceDep):
    personnel = service.log_in(request)

    response.status_code = status.HTTP_204_NO_CONTENT

    return service.set_login_cookies(response, personnel)


@api.post("/logout", status_code=status.HTTP_200_OK)
def log_out(_: Request, response: Response):
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie("personnel_id")

    return response
