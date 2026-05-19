import uuid

from petstore.application.commands.delete_pet_command import DeletePetCommand
from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException, PetNotFoundException
from petstore.domain.repositories.i_pet_repository import IPetRepository


class DeletePetHandler:
    def __init__(self, repository: IPetRepository) -> None:
        self._repository = repository

    def handle(self, command: DeletePetCommand) -> None:
        pet_id = uuid.UUID(command.pet_id)
        requesting_user_id = uuid.UUID(command.requesting_user_id)

        pet = self._repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)
        self._repository.delete(pet_id)
