from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterPetCommand:
    name: str
    last_name: str
    type: str
    owner_id: str
