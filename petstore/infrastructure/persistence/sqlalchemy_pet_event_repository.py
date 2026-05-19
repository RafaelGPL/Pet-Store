import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import text

from petstore.domain.model.event_description import EventDescription
from petstore.domain.model.event_title import EventTitle
from petstore.domain.model.pet_event import PetEvent
from petstore.domain.repositories.i_pet_event_repository import IPetEventRepository
from petstore.infrastructure.persistence.database import get_connection


class SqlAlchemyPetEventRepository(IPetEventRepository):
    def save(self, event: PetEvent) -> None:
        with get_connection() as conn:
            conn.execute(
                text("""
                INSERT INTO pet_events (id, pet_id, title, description, occurred_at)
                VALUES (:id, :pet_id, :title, :description, :occurred_at)
                ON CONFLICT(id) DO UPDATE SET
                    title       = excluded.title,
                    description = excluded.description
                """),
                {
                    "id": str(event.id),
                    "pet_id": str(event.pet_id),
                    "title": event.title.value,
                    "description": event.description.value,
                    "occurred_at": event.occurred_at.isoformat(),
                },
            )
            conn.commit()

    def find_by_id(self, event_id: uuid.UUID) -> Optional[PetEvent]:
        with get_connection() as conn:
            row = conn.execute(
                text("SELECT * FROM pet_events WHERE id = :id"),
                {"id": str(event_id)},
            ).mappings().fetchone()
        return self._to_event(row) if row else None

    def find_by_pet_id(self, pet_id: uuid.UUID) -> List[PetEvent]:
        with get_connection() as conn:
            rows = conn.execute(
                text("SELECT * FROM pet_events WHERE pet_id = :pet_id ORDER BY occurred_at ASC"),
                {"pet_id": str(pet_id)},
            ).mappings().fetchall()
        return [self._to_event(row) for row in rows]

    def delete(self, event_id: uuid.UUID) -> None:
        with get_connection() as conn:
            conn.execute(
                text("DELETE FROM pet_events WHERE id = :id"),
                {"id": str(event_id)},
            )
            conn.commit()

    def _to_event(self, row: Any) -> PetEvent:
        return PetEvent.reconstitute(
            id=uuid.UUID(row["id"]),
            pet_id=uuid.UUID(row["pet_id"]),
            title=EventTitle(value=row["title"]),
            description=EventDescription(value=row["description"]),
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
        )
