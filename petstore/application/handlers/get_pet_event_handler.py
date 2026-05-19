import uuid

from petstore.application.dto.pet_event_dto import PetEventDto
from petstore.application.queries.get_pet_event_query import GetPetEventQuery
from petstore.domain.exceptions.pet_exceptions import (
    PetAccessDeniedException,
    PetEventNotFoundException,
)
from petstore.domain.repositories.i_pet_event_repository import IPetEventRepository
from petstore.domain.repositories.i_pet_repository import IPetRepository


class GetPetEventHandler:
    def __init__(self, event_repository: IPetEventRepository, pet_repository: IPetRepository) -> None:
        self._event_repository = event_repository
        self._pet_repository = pet_repository

    def handle(self, query: GetPetEventQuery) -> PetEventDto:
        event_id = uuid.UUID(query.event_id)
        requesting_user_id = uuid.UUID(query.requesting_user_id)

        event = self._event_repository.find_by_id(event_id)
        if event is None:
            raise PetEventNotFoundException(event_id)

        pet = self._pet_repository.find_by_id(event.pet_id)
        if pet is None or not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(event.pet_id)

        return PetEventDto.from_pet_event(event)
