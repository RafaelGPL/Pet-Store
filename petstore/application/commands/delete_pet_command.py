from dataclasses import dataclass


@dataclass(frozen=True)
class DeletePetCommand:
    pet_id: str
    requesting_user_id: str
