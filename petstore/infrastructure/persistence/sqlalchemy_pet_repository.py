import uuid
from typing import Any, List, Optional

from sqlalchemy import text

from petstore.domain.model.pet import Pet
from petstore.domain.model.pet_name import PetName
from petstore.domain.model.pet_type import PetType
from petstore.domain.repositories.i_pet_repository import IPetRepository
from petstore.infrastructure.persistence.database import get_connection


class SqlAlchemyPetRepository(IPetRepository):
    def save(self, pet: Pet) -> None:
        with get_connection() as conn:
            conn.execute(
                text("""
                INSERT INTO pets (id, first_name, last_name, type)
                VALUES (:id, :first_name, :last_name, :type)
                ON CONFLICT(id) DO UPDATE SET
                    first_name = excluded.first_name,
                    last_name  = excluded.last_name,
                    type       = excluded.type
                """),
                {
                    "id": str(pet.id),
                    "first_name": pet.name.first,
                    "last_name": pet.name.last,
                    "type": pet.type.value,
                },
            )
            # Sync the owner join table: delete existing rows then re-insert.
            conn.execute(
                text("DELETE FROM pet_owners WHERE pet_id = :pet_id"),
                {"pet_id": str(pet.id)},
            )
            if pet.owner_ids:  # pragma: no branch
                conn.execute(
                    text("INSERT INTO pet_owners (pet_id, user_id) VALUES (:pet_id, :user_id)"),
                    [{"pet_id": str(pet.id), "user_id": str(owner_id)} for owner_id in pet.owner_ids],
                )
            conn.commit()

    def find_by_id(self, pet_id: uuid.UUID) -> Optional[Pet]:
        with get_connection() as conn:
            row = conn.execute(
                text("SELECT * FROM pets WHERE id = :id"),
                {"id": str(pet_id)},
            ).mappings().fetchone()
            if row is None:
                return None
            owner_rows = conn.execute(
                text("SELECT user_id FROM pet_owners WHERE pet_id = :pet_id"),
                {"pet_id": str(pet_id)},
            ).mappings().fetchall()
        return self._to_pet(row, owner_rows)

    def find_by_owner(self, user_id: uuid.UUID) -> List[Pet]:
        with get_connection() as conn:
            pet_rows = conn.execute(
                text("""
                SELECT p.*
                FROM pets p
                JOIN pet_owners po ON po.pet_id = p.id
                WHERE po.user_id = :user_id
                """),
                {"user_id": str(user_id)},
            ).mappings().fetchall()
            pets = []
            for row in pet_rows:
                owner_rows = conn.execute(
                    text("SELECT user_id FROM pet_owners WHERE pet_id = :pet_id"),
                    {"pet_id": row["id"]},
                ).mappings().fetchall()
                pets.append(self._to_pet(row, owner_rows))
        return pets

    def delete(self, pet_id: uuid.UUID) -> None:
        with get_connection() as conn:
            conn.execute(
                text("DELETE FROM pets WHERE id = :id"),
                {"id": str(pet_id)},
            )
            conn.commit()

    def _to_pet(self, row: Any, owner_rows: list) -> Pet:
        return Pet.reconstitute(
            id=uuid.UUID(row["id"]),
            name=PetName(first=row["first_name"], last=row["last_name"]),
            type_=PetType(value=row["type"]),
            owner_ids=[uuid.UUID(r["user_id"]) for r in owner_rows],
        )
