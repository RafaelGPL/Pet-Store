import uuid

from petstore.application.commands.register_pet_command import RegisterPetCommand
from petstore.application.dto.pet_dto import PetDto
from petstore.domain.model.pet import Pet
from petstore.domain.model.pet_name import PetName
from petstore.domain.model.pet_type import PetType
from petstore.domain.repositories.i_pet_repository import IPetRepository


class RegisterPetHandler:
    def __init__(self, repository: IPetRepository) -> None:
        self._repository = repository

    def handle(self, command: RegisterPetCommand) -> PetDto:
        pet = Pet.register(
            name=PetName(first=command.name, last=command.last_name),
            type_=PetType(value=command.type),
            initial_owner_id=uuid.UUID(command.owner_id),
        )
        self._repository.save(pet)
        return PetDto.from_pet(pet)
