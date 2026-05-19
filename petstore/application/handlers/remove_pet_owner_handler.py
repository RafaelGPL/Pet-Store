import uuid

from petstore.application.commands.remove_pet_owner_command import RemovePetOwnerCommand
from petstore.application.dto.pet_dto import PetDto
from petstore.domain.exceptions.pet_exceptions import (
    PetAccessDeniedException,
    PetMustHaveAtLeastOneOwnerException,
    PetNotFoundException,
)
from petstore.domain.repositories.i_pet_repository import IPetRepository


class RemovePetOwnerHandler:
    def __init__(self, repository: IPetRepository) -> None:
        self._repository = repository

    def handle(self, command: RemovePetOwnerCommand) -> PetDto:
        pet_id = uuid.UUID(command.pet_id)
        requesting_user_id = uuid.UUID(command.requesting_user_id)
        owner_id = uuid.UUID(command.owner_id)

        pet = self._repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)

        pet.remove_owner(owner_id)
        self._repository.save(pet)
        return PetDto.from_pet(pet)
