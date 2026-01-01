import uuid

from fastapi import APIRouter, Response, status, Cookie, Query

from backend.common import PersonalServiceDep
from backend.schemas import (
    CreatePersonnelRequest,
    SelectPersonnelRequest,
    UpdatePersonnelRequest,
)


api = APIRouter(prefix="/personal", tags=["Personal"])


@api.get("/", status_code=status.HTTP_200_OK)
def get_personnel(
    service: PersonalServiceDep,
    personnel_id: uuid.UUID = Query(title="Personal ID"),
):
    return service.get_by_id(personnel_id)


@api.get("/me", status_code=status.HTTP_200_OK)
def get_personnel_self(
    service: PersonalServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
):
    return service.get_by_id(personnel_id)


@api.get("/all", status_code=status.HTTP_200_OK)
def get_all_personnel(
    service: PersonalServiceDep,
):
    return service.get_all()


@api.post("/", status_code=status.HTTP_201_CREATED)
def create_personnel(
    request: CreatePersonnelRequest,
    service: PersonalServiceDep,
):
    return service.create_personnel(request)


@api.put("/", status_code=status.HTTP_202_ACCEPTED)
def update_personnel(
    request: UpdatePersonnelRequest,
    service: PersonalServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
):
    return service.update_personnel(personnel_id, request)


@api.delete("/", status_code=status.HTTP_200_OK)
def delete_personnel(
    service: PersonalServiceDep,
    id: uuid.UUID = Query(title="Personal ID"),
):
    return service.delete_personnel(id)


@api.put("/select", status_code=status.HTTP_204_NO_CONTENT)
def selected_personnel(
    request: SelectPersonnelRequest,
    response: Response,
    service: PersonalServiceDep,
):
    personnel = service.get_by_id(request.id)

    response.set_cookie("personnel_id", str(personnel.id))
    response.status_code = status.HTTP_204_NO_CONTENT

    return response
