from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdatePetCommand:
    pet_id: str
    requesting_user_id: str
    name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[str] = None
