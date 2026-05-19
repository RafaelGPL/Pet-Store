"""
Database engine bootstrap.

The backend is selected entirely from the DATABASE_URL environment variable:

    sqlite:////absolute/path/to/petstore.db   ← default (local dev)
    postgresql://user:pass@host:5432/dbname   ← production / Heroku

Heroku automatically sets DATABASE_URL when the Postgres add-on is attached.
It uses the legacy "postgres://" scheme; we normalise it to "postgresql://"
so SQLAlchemy 2.x accepts it.
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from sqlalchemy import Engine, create_engine, event, text

_DEFAULT_DB_PATH = Path(__file__).parent / "petstore.db"
_engine: Optional[Engine] = None


def _make_engine() -> Engine:
    url = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")

    # Heroku uses the legacy "postgres://" scheme; SQLAlchemy 2.x requires "postgresql://"
    if url.startswith("postgres://"):  # pragma: no cover
        url = url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(url, pool_pre_ping=True)

    # SQLite does not enforce foreign keys by default — enable on every connection
    if engine.dialect.name == "sqlite":  # pragma: no branch
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, _record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _make_engine()
    return _engine


def _reset_engine() -> None:
    """Dispose the current engine and clear the cache.

    Called by the test suite (via monkeypatch) to force a fresh engine
    pointing at each test's isolated temporary database.
    """
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


@contextmanager
def get_connection():
    """Yield a SQLAlchemy connection. Callers must commit writes explicitly."""
    with get_engine().connect() as conn:
        yield conn


def initialise_schema() -> None:
    """Create all tables if they do not already exist."""
    with get_engine().begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id            TEXT PRIMARY KEY,
                username      TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pets (
                id         TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name  TEXT NOT NULL,
                type       TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pet_owners (
                pet_id  TEXT NOT NULL,
                user_id TEXT NOT NULL,
                PRIMARY KEY (pet_id, user_id),
                FOREIGN KEY (pet_id)  REFERENCES pets(id)  ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pet_events (
                id          TEXT PRIMARY KEY,
                pet_id      TEXT NOT NULL,
                title       TEXT NOT NULL,
                description TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
            )
        """))
