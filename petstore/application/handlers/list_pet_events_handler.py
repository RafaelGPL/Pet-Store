import uuid
from typing import List

from petstore.application.dto.pet_event_dto import PetEventDto
from petstore.application.queries.list_pet_events_query import ListPetEventsQuery
from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException, PetNotFoundException
from petstore.domain.repositories.i_pet_event_repository import IPetEventRepository
from petstore.domain.repositories.i_pet_repository import IPetRepository


class ListPetEventsHandler:
    def __init__(self, event_repository: IPetEventRepository, pet_repository: IPetRepository) -> None:
        self._event_repository = event_repository
        self._pet_repository = pet_repository

    def handle(self, query: ListPetEventsQuery) -> List[PetEventDto]:
        pet_id = uuid.UUID(query.pet_id)
        requesting_user_id = uuid.UUID(query.requesting_user_id)

        pet = self._pet_repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)

        return [PetEventDto.from_pet_event(e) for e in self._event_repository.find_by_pet_id(pet_id)]
