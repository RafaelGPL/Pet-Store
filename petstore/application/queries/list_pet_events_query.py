from dataclasses import dataclass


@dataclass(frozen=True)
class ListPetEventsQuery:
    pet_id: str
    requesting_user_id: str
