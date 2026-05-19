import uuid

from petstore.application.dto.pet_dto import PetDto
from petstore.application.queries.get_pet_query import GetPetQuery
from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException, PetNotFoundException
from petstore.domain.repositories.i_pet_repository import IPetRepository


class GetPetHandler:
    def __init__(self, repository: IPetRepository) -> None:
        self._repository = repository

    def handle(self, query: GetPetQuery) -> PetDto:
        pet_id = uuid.UUID(query.pet_id)
        requesting_user_id = uuid.UUID(query.requesting_user_id)

        pet = self._repository.find_by_id(pet_id)
        if pet is None:
            raise PetNotFoundException(pet_id)
        if not pet.is_owned_by(requesting_user_id):
            raise PetAccessDeniedException(pet_id)
        return PetDto.from_pet(pet)
