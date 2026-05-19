import sqlite3
import uuid
from typing import Optional

from identity.domain.model.user import User
from identity.domain.model.username import Username
from identity.domain.repositories.i_user_repository import IUserRepository
from petstore.infrastructure.persistence.database import get_connection


class SqliteUserRepository(IUserRepository):
    def save(self, user: User) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (id, username, password_hash)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username      = excluded.username,
                    password_hash = excluded.password_hash
                """,
                (str(user.id), user.username.value, user.password_hash),
            )
            conn.commit()

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (str(user_id),)
            ).fetchone()
        return self._to_user(row) if row else None

    def find_by_username(self, username: str) -> Optional[User]:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username.lower(),)
            ).fetchone()
        return self._to_user(row) if row else None

    def _to_user(self, row: sqlite3.Row) -> User:
        return User.reconstitute(
            id=uuid.UUID(row["id"]),
            username=Username(value=row["username"]),
            password_hash=row["password_hash"],
        )
