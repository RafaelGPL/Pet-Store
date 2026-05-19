from dataclasses import dataclass


@dataclass(frozen=True)
class AddPetEventCommand:
    pet_id: str
    requesting_user_id: str
    title: str
    description: str
