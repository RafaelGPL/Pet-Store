from dataclasses import dataclass


@dataclass(frozen=True)
class GetPetQuery:
    pet_id: str
    requesting_user_id: str
