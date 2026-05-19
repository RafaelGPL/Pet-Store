from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from identity.presentation.http.dependencies import get_current_user_id
from petstore.application.commands.add_pet_event_command import AddPetEventCommand
from petstore.application.commands.delete_pet_event_command import DeletePetEventCommand
from petstore.application.handlers.add_pet_event_handler import AddPetEventHandler
from petstore.application.handlers.delete_pet_event_handler import DeletePetEventHandler
from petstore.application.handlers.get_pet_event_handler import GetPetEventHandler
from petstore.application.handlers.list_pet_events_handler import ListPetEventsHandler
from petstore.application.queries.get_pet_event_query import GetPetEventQuery
from petstore.application.queries.list_pet_events_query import ListPetEventsQuery
from petstore.domain.exceptions.pet_exceptions import (
    PetAccessDeniedException,
    PetEventNotFoundException,
    PetNotFoundException,
)
from petstore.infrastructure.persistence.sqlite_pet_event_repository import SqlitePetEventRepository
from petstore.infrastructure.persistence.sqlite_pet_repository import SqlitePetRepository

router = APIRouter(redirect_slashes=False)


# --- Pydantic request / response models ---


class AddPetEventRequest(BaseModel):
    title: str
    description: str


class PetEventResponse(BaseModel):
    id: str
    pet_id: str
    title: str
    description: str
    occurred_at: str


# --- dependency factories ---


def _pet_repo() -> SqlitePetRepository:
    return SqlitePetRepository()


def _event_repo() -> SqlitePetEventRepository:
    return SqlitePetEventRepository()


def _event_response(dto) -> PetEventResponse:
    return PetEventResponse(
        id=dto.id,
        pet_id=dto.pet_id,
        title=dto.title,
        description=dto.description,
        occurred_at=dto.occurred_at,
    )


# --- routes ---


@router.post(
    "/pets/{pet_id}/events",
    status_code=status.HTTP_201_CREATED,
    response_model=PetEventResponse,
    tags=["events"],
)
def add_pet_event(
    pet_id: str,
    body: AddPetEventRequest,
    user_id: str = Depends(get_current_user_id),
):
    try:
        dto = AddPetEventHandler(_pet_repo(), _event_repo()).handle(
            AddPetEventCommand(
                pet_id=pet_id,
                requesting_user_id=user_id,
                title=body.title,
                description=body.description,
            )
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _event_response(dto)


@router.get("/pets/{pet_id}/events", response_model=List[PetEventResponse], tags=["events"])
def list_pet_events(pet_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        dtos = ListPetEventsHandler(_event_repo(), _pet_repo()).handle(
            ListPetEventsQuery(pet_id=pet_id, requesting_user_id=user_id)
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return [_event_response(d) for d in dtos]


@router.get(
    "/pets/{pet_id}/events/{event_id}",
    response_model=PetEventResponse,
    tags=["events"],
)
def get_pet_event(pet_id: str, event_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        dto = GetPetEventHandler(_event_repo(), _pet_repo()).handle(
            GetPetEventQuery(event_id=event_id, requesting_user_id=user_id)
        )
    except PetEventNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _event_response(dto)


@router.delete(
    "/pets/{pet_id}/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["events"],
)
def delete_pet_event(pet_id: str, event_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        DeletePetEventHandler(_event_repo(), _pet_repo()).handle(
            DeletePetEventCommand(event_id=event_id, requesting_user_id=user_id)
        )
    except PetEventNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
