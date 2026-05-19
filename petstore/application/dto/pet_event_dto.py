from dataclasses import dataclass

from petstore.domain.model.pet_event import PetEvent


@dataclass(frozen=True)
class PetEventDto:
    id: str
    pet_id: str
    title: str
    description: str
    occurred_at: str

    @staticmethod
    def from_pet_event(event: PetEvent) -> "PetEventDto":
        return PetEventDto(
            id=str(event.id),
            pet_id=str(event.pet_id),
            title=event.title.value,
            description=event.description.value,
            occurred_at=event.occurred_at.isoformat(),
        )
