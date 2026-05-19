from dataclasses import dataclass


@dataclass(frozen=True)
class DeletePetEventCommand:
    event_id: str
    requesting_user_id: str
