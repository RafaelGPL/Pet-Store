"""
Shared fixtures for the Pet Store test suite.

Key design decisions:
- Every test gets a fresh SQLite database in a temp directory.
- BcryptPasswordService is patched to use 4 rounds (vs default 12) so the
  suite runs in seconds rather than minutes.
- `initialise_schema()` is called via the FastAPI lifespan, so it always hits
  the monkeypatched DB_PATH — no real database is ever created during tests.
"""

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

import petstore.infrastructure.persistence.database as _db_module
from identity.infrastructure.security.bcrypt_password_service import BcryptPasswordService

_FAST_CRYPT = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    """Redirect every DB connection to a per-test temp file and use fast bcrypt."""
    monkeypatch.setattr(_db_module, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(BcryptPasswordService, "_context", _FAST_CRYPT)


@pytest.fixture
def client(_isolated_db):
    from main import app

    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Convenience fixtures — register two users and expose their tokens / IDs
# ---------------------------------------------------------------------------


@pytest.fixture
def alice(client):
    r = client.post("/auth/register", json={"username": "alice", "password": "pw"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def bob(client):
    r = client.post("/auth/register", json={"username": "bob", "password": "pw"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def alice_headers(alice):
    return {"Authorization": f"Bearer {alice['access_token']}"}


@pytest.fixture
def bob_headers(bob):
    return {"Authorization": f"Bearer {bob['access_token']}"}


@pytest.fixture
def alice_pet(client, alice_headers):
    """Register a pet owned by Alice and return the response body."""
    r = client.post(
        "/pets",
        json={"name": "Whiskers", "last_name": "McFluff", "type": "cat"},
        headers=alice_headers,
    )
    assert r.status_code == 201
    return r.json()
