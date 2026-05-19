from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from identity.domain.exceptions.user_exceptions import UserNotFoundException
from identity.infrastructure.persistence.sqlite_user_repository import SqliteUserRepository
from identity.presentation.http.dependencies import get_current_user_id
from petstore.application.commands.add_pet_owner_command import AddPetOwnerCommand
from petstore.application.commands.delete_pet_command import DeletePetCommand
from petstore.application.commands.register_pet_command import RegisterPetCommand
from petstore.application.commands.remove_pet_owner_command import RemovePetOwnerCommand
from petstore.application.commands.update_pet_command import UpdatePetCommand
from petstore.application.handlers.add_pet_owner_handler import AddPetOwnerHandler
from petstore.application.handlers.delete_pet_handler import DeletePetHandler
from petstore.application.handlers.get_pet_handler import GetPetHandler
from petstore.application.handlers.list_pets_handler import ListPetsHandler
from petstore.application.handlers.register_pet_handler import RegisterPetHandler
from petstore.application.handlers.remove_pet_owner_handler import RemovePetOwnerHandler
from petstore.application.handlers.update_pet_handler import UpdatePetHandler
from petstore.application.queries.get_pet_query import GetPetQuery
from petstore.application.queries.list_pets_query import ListPetsQuery
from petstore.domain.exceptions.pet_exceptions import (
    PetAccessDeniedException,
    PetMustHaveAtLeastOneOwnerException,
    PetNotFoundException,
)
from petstore.infrastructure.persistence.sqlite_pet_repository import SqlitePetRepository

router = APIRouter(prefix="/pets", tags=["pets"], redirect_slashes=False)


# --- Pydantic request / response models ---


class RegisterPetRequest(BaseModel):
    name: str = Field(min_length=1, examples=["Whiskers"], description="Pet's first name.")
    last_name: str = Field(min_length=1, examples=["McFluff"], description="Pet's last name.")
    type: str = Field(min_length=1, examples=["cat"], description="Species or breed (e.g. cat, dog, rabbit).")

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Whiskers", "last_name": "McFluff", "type": "cat"}
        }
    }


class UpdatePetRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, examples=["Shadow"], description="New first name.")
    last_name: Optional[str] = Field(None, min_length=1, examples=["Nightpaw"], description="New last name.")
    type: Optional[str] = Field(None, min_length=1, examples=["cat"], description="New species/breed.")

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Shadow"}
        }
    }


class AddOwnerRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        examples=["bob"],
        description="Username of the registered user to add as a co-owner.",
    )

    model_config = {
        "json_schema_extra": {"example": {"username": "bob"}}
    }


class PetResponse(BaseModel):
    id: str = Field(description="UUID of the pet.")
    name: str = Field(description="Pet's first name.")
    last_name: str = Field(description="Pet's last name.")
    type: str = Field(description="Species or breed.")
    owner_ids: Tuple[str, ...] = Field(description="UUIDs of all current owners.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Whiskers",
                "last_name": "McFluff",
                "type": "cat",
                "owner_ids": ["a1b2c3d4-0000-0000-0000-000000000001"],
            }
        }
    }


# --- dependency factories ---


def _pet_repo() -> SqlitePetRepository:
    return SqlitePetRepository()


def _user_repo() -> SqliteUserRepository:
    return SqliteUserRepository()


def _pet_response(dto) -> PetResponse:
    return PetResponse(
        id=dto.id,
        name=dto.name,
        last_name=dto.last_name,
        type=dto.type,
        owner_ids=dto.owner_ids,
    )


# --- routes ---


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PetResponse,
    summary="Register a pet",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        422: {"description": "Validation error — name or type is blank."},
    },
)
def register_pet(
    body: RegisterPetRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Register a new pet. The authenticated user becomes its sole initial owner.

    Fields:
    - **name** / **last_name**: non-empty strings.
    - **type**: free-form species or breed string (e.g. `cat`, `dog`, `parrot`).
    """
    try:
        dto = RegisterPetHandler(_pet_repo()).handle(
            RegisterPetCommand(
                name=body.name,
                last_name=body.last_name,
                type=body.type,
                owner_id=user_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _pet_response(dto)


@router.get(
    "",
    response_model=List[PetResponse],
    summary="List my pets",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
    },
)
def list_pets(user_id: str = Depends(get_current_user_id)):
    """
    Return all pets the authenticated user currently owns (including co-owned pets).
    Pets owned exclusively by other users are never returned.
    """
    dtos = ListPetsHandler(_pet_repo()).handle(ListPetsQuery(requesting_user_id=user_id))
    return [_pet_response(d) for d in dtos]


@router.get(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Get a pet",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found."},
    },
)
def get_pet(pet_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieve a single pet by ID. Returns 403 if the authenticated user is not an owner.
    """
    try:
        dto = GetPetHandler(_pet_repo()).handle(
            GetPetQuery(pet_id=pet_id, requesting_user_id=user_id)
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _pet_response(dto)


@router.patch(
    "/{pet_id}",
    response_model=PetResponse,
    summary="Update a pet",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found."},
        422: {"description": "Validation error — a provided field is blank."},
    },
)
def update_pet(
    pet_id: str,
    body: UpdatePetRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Partially update a pet's **name**, **last_name**, and/or **type**.
    Omit any field to leave it unchanged. Requires ownership.
    """
    try:
        dto = UpdatePetHandler(_pet_repo()).handle(
            UpdatePetCommand(
                pet_id=pet_id,
                requesting_user_id=user_id,
                name=body.name,
                last_name=body.last_name,
                type=body.type,
            )
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _pet_response(dto)


@router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a pet",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found."},
    },
)
def delete_pet(pet_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Permanently delete a pet and all its events.
    Requires ownership. Cascades to all associated events.
    """
    try:
        DeletePetHandler(_pet_repo()).handle(
            DeletePetCommand(pet_id=pet_id, requesting_user_id=user_id)
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post(
    "/{pet_id}/owners",
    response_model=PetResponse,
    summary="Add a co-owner",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found, or target username does not exist."},
        422: {"description": "Validation error."},
    },
)
def add_owner(
    pet_id: str,
    body: AddOwnerRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Grant co-ownership of a pet to another registered user.

    - The caller must already be an owner of the pet.
    - **username** must belong to an existing account.
    - Adding a user who is already an owner is a no-op.
    """
    try:
        dto = AddPetOwnerHandler(_pet_repo(), _user_repo()).handle(
            AddPetOwnerCommand(
                pet_id=pet_id,
                requesting_user_id=user_id,
                new_owner_username=body.username,
            )
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except UserNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _pet_response(dto)


@router.delete(
    "/{pet_id}/owners/{owner_id}",
    response_model=PetResponse,
    summary="Remove a co-owner",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Authenticated user is not an owner of this pet."},
        404: {"description": "Pet not found."},
        409: {"description": "Cannot remove the last remaining owner."},
    },
)
def remove_owner(
    pet_id: str,
    owner_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Remove a co-owner from a pet.

    - The caller must be an owner (they may remove themselves or others).
    - Returns **409** if removing this owner would leave the pet with no owners.
    - **owner_id** is the UUID of the user to remove (not their username).
    """
    try:
        dto = RemovePetOwnerHandler(_pet_repo()).handle(
            RemovePetOwnerCommand(
                pet_id=pet_id,
                requesting_user_id=user_id,
                owner_id=owner_id,
            )
        )
    except PetNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PetAccessDeniedException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except PetMustHaveAtLeastOneOwnerException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return _pet_response(dto)
