import uuid
from datetime import datetime, timezone

from petstore.domain.model.event_description import EventDescription
from petstore.domain.model.event_title import EventTitle


class PetEvent:
    def __init__(
        self,
        id: uuid.UUID,
        pet_id: uuid.UUID,
        title: EventTitle,
        description: EventDescription,
        occurred_at: datetime,
    ) -> None:
        self._id = id
        self._pet_id = pet_id
        self._title = title
        self._description = description
        self._occurred_at = occurred_at

    # --- factories ---

    @classmethod
    def record(
        cls,
        pet_id: uuid.UUID,
        title: EventTitle,
        description: EventDescription,
    ) -> "PetEvent":
        return cls(
            id=uuid.uuid4(),
            pet_id=pet_id,
            title=title,
            description=description,
            occurred_at=datetime.now(timezone.utc),
        )

    @classmethod
    def reconstitute(
        cls,
        id: uuid.UUID,
        pet_id: uuid.UUID,
        title: EventTitle,
        description: EventDescription,
        occurred_at: datetime,
    ) -> "PetEvent":
        return cls(id=id, pet_id=pet_id, title=title, description=description, occurred_at=occurred_at)

    # --- properties ---

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def pet_id(self) -> uuid.UUID:
        return self._pet_id

    @property
    def title(self) -> EventTitle:
        return self._title

    @property
    def description(self) -> EventDescription:
        return self._description

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at
