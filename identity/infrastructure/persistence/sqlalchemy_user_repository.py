import uuid
from typing import Any, Optional

from sqlalchemy import text

from identity.domain.model.user import User
from identity.domain.model.username import Username
from identity.domain.repositories.i_user_repository import IUserRepository
from petstore.infrastructure.persistence.database import get_connection


class SqlAlchemyUserRepository(IUserRepository):
    def save(self, user: User) -> None:
        with get_connection() as conn:
            conn.execute(
                text("""
                INSERT INTO users (id, username, password_hash)
                VALUES (:id, :username, :password_hash)
                ON CONFLICT(id) DO UPDATE SET
                    username      = excluded.username,
                    password_hash = excluded.password_hash
                """),
                {
                    "id": str(user.id),
                    "username": user.username.value,
                    "password_hash": user.password_hash,
                },
            )
            conn.commit()

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        with get_connection() as conn:
            row = conn.execute(
                text("SELECT * FROM users WHERE id = :id"),
                {"id": str(user_id)},
            ).mappings().fetchone()
        return self._to_user(row) if row else None

    def find_by_username(self, username: str) -> Optional[User]:
        with get_connection() as conn:
            row = conn.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username": username.lower()},
            ).mappings().fetchone()
        return self._to_user(row) if row else None

    def _to_user(self, row: Any) -> User:
        return User.reconstitute(
            id=uuid.UUID(row["id"]),
            username=Username(value=row["username"]),
            password_hash=row["password_hash"],
        )
