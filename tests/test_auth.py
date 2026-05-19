"""Tests for /auth/* endpoints — registration, login, token validation."""


class TestRegister:
    def test_success_returns_token(self, client):
        r = client.post("/auth/register", json={"username": "alice", "password": "pw"})
        assert r.status_code == 201
        body = r.json()
        assert body["username"] == "alice"
        assert body["token_type"] == "bearer"
        assert body["access_token"]
        assert body["user_id"]

    def test_duplicate_username_returns_409(self, client):
        client.post("/auth/register", json={"username": "alice", "password": "pw"})
        r = client.post("/auth/register", json={"username": "alice", "password": "other"})
        assert r.status_code == 409

    def test_empty_username_returns_422(self, client):
        r = client.post("/auth/register", json={"username": "   ", "password": "pw"})
        assert r.status_code == 422

    def test_username_too_short_returns_422(self, client):
        r = client.post("/auth/register", json={"username": "ab", "password": "pw"})
        assert r.status_code == 422

    def test_username_too_long_returns_422(self, client):
        r = client.post("/auth/register", json={"username": "a" * 51, "password": "pw"})
        assert r.status_code == 422

    def test_username_invalid_chars_returns_422(self, client):
        r = client.post("/auth/register", json={"username": "bad user!", "password": "pw"})
        assert r.status_code == 422


class TestToken:
    def test_correct_credentials_return_token(self, client):
        client.post("/auth/register", json={"username": "alice", "password": "secret"})
        r = client.post("/auth/token", data={"username": "alice", "password": "secret"})
        assert r.status_code == 200
        assert r.json()["token_type"] == "bearer"

    def test_wrong_password_returns_401(self, client):
        client.post("/auth/register", json={"username": "alice", "password": "secret"})
        r = client.post("/auth/token", data={"username": "alice", "password": "wrong"})
        assert r.status_code == 401

    def test_unknown_username_returns_401(self, client):
        r = client.post("/auth/token", data={"username": "nobody", "password": "pw"})
        assert r.status_code == 401


class TestMe:
    def test_success(self, client, alice, alice_headers):
        r = client.get("/auth/me", headers=alice_headers)
        assert r.status_code == 200
        assert r.json()["username"] == "alice"

    def test_no_token_returns_401(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_invalid_token_returns_401(self, client):
        r = client.get("/auth/me", headers={"Authorization": "Bearer garbage.token.here"})
        assert r.status_code == 401

    def test_deleted_user_returns_404(self, client, alice, alice_headers):
        """Token is valid but the user record has been removed — expect 404."""
        from sqlalchemy import text

        from petstore.infrastructure.persistence.database import get_connection

        with get_connection() as conn:
            conn.execute(text("DELETE FROM users"))
            conn.commit()

        r = client.get("/auth/me", headers=alice_headers)
        assert r.status_code == 404
