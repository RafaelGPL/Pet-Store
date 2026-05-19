import uuid

from petstore.application.commands.add_pet_event_command import AddPetEventCommand
from petstore.application.dto.pet_event_dto import PetEventDto
from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException, PetNotFoundException
from petstore.domain.model.event_description import EventDescription
from petstore.domain.model.event_title import EventTitle
from petstore.domain.model.pet_event import PetEvent
from petstore.domain.repositories.i_pet_event_repository import IPetEventRepository
from petstore.domain.repositories.i_pet_repository import IPetRepository


class AddPetEventHandler:
    def __init__(self, pet_repository: IPetRepository, event_repository: IPetEventRepository) -> None:
        self._pet_repository = pet_repository
        self._event_repository = event_repository

    def handle(self, command: AddPetEventCommand) -> PetEventDto:
        pet_id = uuid.UUID(command.pet_id)
        requesting_user_id = uuid.UUID(command.requesting_user_id)

        pet = self._pet_repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)

        event = PetEvent.record(
            pet_id=pet_id,
            title=EventTitle(value=command.title),
            description=EventDescription(value=command.description),
        )
        self._event_repository.save(event)
        return PetEventDto.from_pet_event(event)
