import uuid

from petstore.application.commands.update_pet_command import UpdatePetCommand
from petstore.application.dto.pet_dto import PetDto
from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException, PetNotFoundException
from petstore.domain.model.pet_name import PetName
from petstore.domain.model.pet_type import PetType
from petstore.domain.repositories.i_pet_repository import IPetRepository


class UpdatePetHandler:
    def __init__(self, repository: IPetRepository) -> None:
        self._repository = repository

    def handle(self, command: UpdatePetCommand) -> PetDto:
        pet_id = uuid.UUID(command.pet_id)
        requesting_user_id = uuid.UUID(command.requesting_user_id)

        pet = self._repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)

        if command.name is not None or command.last_name is not None:
            new_first = command.name if command.name is not None else pet.name.first
            new_last = command.last_name if command.last_name is not None else pet.name.last
            pet.rename(PetName(first=new_first, last=new_last))

        if command.type is not None:
            pet.change_type(PetType(value=command.type))

        self._repository.save(pet)
        return PetDto.from_pet(pet)
