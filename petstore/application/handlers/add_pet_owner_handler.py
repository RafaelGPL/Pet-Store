import uuid

from identity.domain.exceptions.user_exceptions import UserNotFoundException
from identity.domain.repositories.i_user_repository import IUserRepository
from petstore.application.commands.add_pet_owner_command import AddPetOwnerCommand
from petstore.application.dto.pet_dto import PetDto
from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException, PetNotFoundException
from petstore.domain.repositories.i_pet_repository import IPetRepository


class AddPetOwnerHandler:
    def __init__(self, pet_repository: IPetRepository, user_repository: IUserRepository) -> None:
        self._pet_repository = pet_repository
        self._user_repository = user_repository

    def handle(self, command: AddPetOwnerCommand) -> PetDto:
        pet_id = uuid.UUID(command.pet_id)
        requesting_user_id = uuid.UUID(command.requesting_user_id)

        pet = self._pet_repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)

        new_owner = self._user_repository.find_by_username(command.new_owner_username.lower())
        if new_owner is None:
            raise UserNotFoundException(command.new_owner_username)

        pet.add_owner(new_owner.id)
        self._pet_repository.save(pet)
        return PetDto.from_pet(pet)
