from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.common import CurrentPersonnelID, PersonalServiceDep
from src.schemas import (
    PersonnelSchema,
    SlimPersonnelSchema,
    UpdatePersonnelDetailsRequest,
    UpdatePersonnelEmailRequest,
    UpdatePersonnelPasswordRequest,
)


api = APIRouter(prefix="/personal", tags=["Personal"])


@api.get("/", status_code=status.HTTP_200_OK, response_model=PersonnelSchema)
def get_personnel(service: PersonalServiceDep, personnel_id: UUID):
    personnel = service.get_by_id(personnel_id)

    if personnel:
        return personnel

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Personnel does not exist"
    )


@api.get("/me", status_code=status.HTTP_200_OK, response_model=PersonnelSchema)
def get_personnel_self(
    service: PersonalServiceDep,
    personnel_id: CurrentPersonnelID,
):
    return service.personnel_exists(personnel_id)


@api.get(
    "/all", status_code=status.HTTP_200_OK, response_model=list[SlimPersonnelSchema]
)
def get_all_personnel(service: PersonalServiceDep):
    return service.get_all()


@api.delete("/", status_code=status.HTTP_200_OK)
def delete_personnel(
    service: PersonalServiceDep,
    personnel_id: UUID = Query(title="Personal ID"),
):
    personnel = service.personnel_exists(personnel_id)

    return service.delete_personnel(personnel)


@api.put(
    "/me/details",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SlimPersonnelSchema,
)
def update_personnel_details(
    request: UpdatePersonnelDetailsRequest,
    service: PersonalServiceDep,
    personnel_id: CurrentPersonnelID,
):
    personnel = service.personnel_exists(personnel_id)

    return service.update_personnel_details(personnel, request)


@api.put(
    "/me/email", status_code=status.HTTP_202_ACCEPTED, response_model=PersonnelSchema
)
def update_personnel_email(
    request: UpdatePersonnelEmailRequest,
    service: PersonalServiceDep,
    personnel_id: CurrentPersonnelID,
):
    personnel = service.personnel_exists(personnel_id)

    return service.update_personnel_email(personnel, request)


@api.put(
    "/me/password", status_code=status.HTTP_202_ACCEPTED, response_model=PersonnelSchema
)
def update_personnel_password(
    request: UpdatePersonnelPasswordRequest,
    service: PersonalServiceDep,
    personnel_id: CurrentPersonnelID,
):
    personnel = service.personnel_exists(personnel_id)

    return service.update_personnel_password(personnel, request)
