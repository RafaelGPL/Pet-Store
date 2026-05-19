from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

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
    name: str
    last_name: str
    type: str


class UpdatePetRequest(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[str] = None


class AddOwnerRequest(BaseModel):
    username: str


class PetResponse(BaseModel):
    id: str
    name: str
    last_name: str
    type: str
    owner_ids: Tuple[str, ...]


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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PetResponse)
def register_pet(
    body: RegisterPetRequest,
    user_id: str = Depends(get_current_user_id),
):
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


@router.get("", response_model=List[PetResponse])
def list_pets(user_id: str = Depends(get_current_user_id)):
    dtos = ListPetsHandler(_pet_repo()).handle(ListPetsQuery(requesting_user_id=user_id))
    return [_pet_response(d) for d in dtos]


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: str, user_id: str = Depends(get_current_user_id)):
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


@router.patch("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: str,
    body: UpdatePetRequest,
    user_id: str = Depends(get_current_user_id),
):
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


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: str, user_id: str = Depends(get_current_user_id)):
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


@router.post("/{pet_id}/owners", response_model=PetResponse)
def add_owner(
    pet_id: str,
    body: AddOwnerRequest,
    user_id: str = Depends(get_current_user_id),
):
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


@router.delete("/{pet_id}/owners/{owner_id}", response_model=PetResponse)
def remove_owner(
    pet_id: str,
    owner_id: str,
    user_id: str = Depends(get_current_user_id),
):
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
