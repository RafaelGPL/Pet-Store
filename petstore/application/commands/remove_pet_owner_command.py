from dataclasses import dataclass


@dataclass(frozen=True)
class RemovePetOwnerCommand:
    pet_id: str
    requesting_user_id: str
    owner_id: str
