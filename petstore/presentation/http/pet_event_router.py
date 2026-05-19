from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

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
    title: str = Field(
        min_length=1,
        max_length=200,
        examples=["Annual vet check-up"],
        description="Short title for the event (max 200 characters).",
    )
    description: str = Field(
        min_length=1,
        examples=["Routine wellness exam. All vitals normal. Rabies booster administered."],
        description="Full description of what happened.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Annual vet check-up",
                "description": "Routine wellness exam. All vitals normal. Rabies booster administered.",
            }
        }
    }


class PetEventResponse(BaseModel):
    id: str = Field(description="UUID of the event.")
    pet_id: str = Field(description="UUID of the parent pet.")
    title: str = Field(description="Short title of the event.")
    description: str = Field(description="Full description of the event.")
    occurred_at: str = Field(description="ISO 8601 UTC timestamp of when the event was recorded.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "pet_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "Annual vet check-up",
                "description": "Routine wellness exam. All vitals normal.",
                "occurred_at": "2026-05-19T14:30:00.000000",
            }
        }
    }


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
    summary="Record a pet event",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found."},
        422: {"description": "Validation error — title or description is blank."},
    },
)
def add_pet_event(
    pet_id: str,
    body: AddPetEventRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Record a new timestamped event for a pet (e.g. vet visit, vaccination, grooming).

    - **title**: 1–200 characters.
    - **description**: any non-empty string.
    - `occurred_at` is set automatically to the current UTC time.

    Requires ownership of the parent pet.
    """
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


@router.get(
    "/pets/{pet_id}/events",
    response_model=List[PetEventResponse],
    tags=["events"],
    summary="List events for a pet",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found."},
    },
)
def list_pet_events(pet_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Return all recorded events for a pet, ordered by insertion time (oldest first).
    Requires ownership of the parent pet.
    """
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
    summary="Get a pet event",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Event not found."},
    },
)
def get_pet_event(pet_id: str, event_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieve a single event by ID.
    Ownership of the parent pet is required even if you know the event ID.
    """
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
    summary="Delete a pet event",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Event not found."},
    },
)
def delete_pet_event(pet_id: str, event_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Permanently delete an event. Requires ownership of the parent pet.
    Returns **204 No Content** on success.
    """
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
