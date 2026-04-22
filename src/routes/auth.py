import uuid

from fastapi import APIRouter, status

from src.common import AuthServiceDep
from src.schemas import CreatePersonnelRequest, LogInRequest


api = APIRouter(prefix="/auth", tags=["Auth"])


@api.post("/register", status_code=status.HTTP_201_CREATED)
def register_personnel(request: CreatePersonnelRequest, service: AuthServiceDep):
    return service.register(request)


@api.post("/login", status_code=status.HTTP_200_OK)
def log_in(request: LogInRequest, service: AuthServiceDep):
    return service.log_in(request)
