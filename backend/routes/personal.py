import uuid

from fastapi import APIRouter, HTTPException, Response, status, Cookie, Query

from backend.common import PersonalServiceDep
from backend.schemas import (
    CreatePersonnelRequest,
    SelectPersonnelRequest,
    UpdatePersonnelRequest,
)


api = APIRouter(prefix="/personal", tags=["Personal"])


@api.get("/", status_code=status.HTTP_200_OK)
def get_personnel(
    service: PersonalServiceDep, personnel_id: uuid.UUID = Query(title="Personal ID")
):
    personnel = service.get_by_id(personnel_id)

    if personnel:
        return personnel

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Personnel does not exist"
    )


@api.get("/me", status_code=status.HTTP_200_OK)
def get_personnel_self(
    service: PersonalServiceDep,
    personnel_id: uuid.UUID = Cookie("personnel_id", include_in_schema=False),
):
    return service.personnel_exists(personnel_id)


@api.get("/all", status_code=status.HTTP_200_OK)
def get_all_personnel(service: PersonalServiceDep):
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
    personnel = service.personnel_exists(personnel_id)

    return service.update_personnel(personnel, request)


@api.delete("/", status_code=status.HTTP_200_OK)
def delete_personnel(
    service: PersonalServiceDep,
    id: uuid.UUID = Query(title="Personal ID"),
):
    personnel = service.personnel_exists(id)

    return service.delete_personnel(personnel)


@api.put("/select", status_code=status.HTTP_204_NO_CONTENT)
def selected_personnel(
    request: SelectPersonnelRequest,
    response: Response,
    service: PersonalServiceDep,
):
    personnel = service.personnel_exists(request.id)

    print(personnel)

    response.set_cookie("personnel_id", str(personnel.id))
    response.status_code = status.HTTP_204_NO_CONTENT

    return response
