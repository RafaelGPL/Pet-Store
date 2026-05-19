import uuid
from typing import List

from petstore.application.dto.pet_dto import PetDto
from petstore.application.queries.list_pets_query import ListPetsQuery
from petstore.domain.repositories.i_pet_repository import IPetRepository


class ListPetsHandler:
    def __init__(self, repository: IPetRepository) -> None:
        self._repository = repository

    def handle(self, query: ListPetsQuery) -> List[PetDto]:
        user_id = uuid.UUID(query.requesting_user_id)
        return [PetDto.from_pet(pet) for pet in self._repository.find_by_owner(user_id)]
