from typing import Tuple
from dataclasses import dataclass

from petstore.domain.model.pet import Pet


@dataclass(frozen=True)
class PetDto:
    id: str
    name: str
    last_name: str
    type: str
    owner_ids: Tuple[str, ...]

    @staticmethod
    def from_pet(pet: Pet) -> "PetDto":
        return PetDto(
            id=str(pet.id),
            name=pet.name.first,
            last_name=pet.name.last,
            type=pet.type.value,
            owner_ids=tuple(str(uid) for uid in pet.owner_ids),
        )
