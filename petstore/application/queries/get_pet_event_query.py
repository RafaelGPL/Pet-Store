from dataclasses import dataclass


@dataclass(frozen=True)
class GetPetEventQuery:
    event_id: str
    requesting_user_id: str
