import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class PetRegisteredEvent:
    pet_id: uuid.UUID
    owner_id: uuid.UUID
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
