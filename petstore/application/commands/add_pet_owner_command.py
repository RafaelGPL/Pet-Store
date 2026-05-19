from dataclasses import dataclass


@dataclass(frozen=True)
class AddPetOwnerCommand:
    pet_id: str
    requesting_user_id: str
    new_owner_username: str
