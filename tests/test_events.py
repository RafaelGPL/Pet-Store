"""Tests for /pets/{id}/events/* endpoints — event CRUD and access control."""

import uuid

_UNKNOWN_ID = str(uuid.uuid4())
_BAD_UUID = "not-a-uuid"


class TestAddEvent:
    def test_success(self, client, alice_headers, alice_pet):
        r = client.post(
            f"/pets/{alice_pet['id']}/events",
            json={"title": "Vet visit", "description": "All clear"},
            headers=alice_headers,
        )
        assert r.status_code == 201
        body = r.json()
        assert body["title"] == "Vet visit"
        assert body["pet_id"] == alice_pet["id"]
        assert body["occurred_at"]

    def test_pet_not_found_returns_404(self, client, alice_headers):
        r = client.post(
            f"/pets/{_UNKNOWN_ID}/events",
            json={"title": "T", "description": "D"},
            headers=alice_headers,
        )
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_pet, bob_headers):
        r = client.post(
            f"/pets/{alice_pet['id']}/events",
            json={"title": "T", "description": "D"},
            headers=bob_headers,
        )
        assert r.status_code == 403

    def test_whitespace_title_returns_422(self, client, alice_headers, alice_pet):
        r = client.post(
            f"/pets/{alice_pet['id']}/events",
            json={"title": "  ", "description": "D"},
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_whitespace_description_returns_422(self, client, alice_headers, alice_pet):
        r = client.post(
            f"/pets/{alice_pet['id']}/events",
            json={"title": "T", "description": "  "},
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_invalid_uuid_returns_422(self, client, alice_headers):
        r = client.post(
            f"/pets/{_BAD_UUID}/events",
            json={"title": "T", "description": "D"},
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        r = client.post(
            f"/pets/{alice_pet['id']}/events",
            json={"title": "T", "description": "D"},
        )
        assert r.status_code == 401


class TestListEvents:
    def test_success_empty(self, client, alice_headers, alice_pet):
        r = client.get(f"/pets/{alice_pet['id']}/events", headers=alice_headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_success_with_events(self, client, alice_headers, alice_pet):
        client.post(
            f"/pets/{alice_pet['id']}/events",
            json={"title": "A", "description": "D"},
            headers=alice_headers,
        )
        r = client.get(f"/pets/{alice_pet['id']}/events", headers=alice_headers)
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_pet_not_found_returns_404(self, client, alice_headers):
        r = client.get(f"/pets/{_UNKNOWN_ID}/events", headers=alice_headers)
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_pet, bob_headers):
        r = client.get(f"/pets/{alice_pet['id']}/events", headers=bob_headers)
        assert r.status_code == 403

    def test_invalid_uuid_returns_422(self, client, alice_headers):
        r = client.get(f"/pets/{_BAD_UUID}/events", headers=alice_headers)
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        assert client.get(f"/pets/{alice_pet['id']}/events").status_code == 401


class TestGetEvent:
    def _create_event(self, client, pet_id, headers):
        r = client.post(
            f"/pets/{pet_id}/events",
            json={"title": "Vet visit", "description": "All clear"},
            headers=headers,
        )
        return r.json()

    def test_success(self, client, alice_headers, alice_pet):
        ev = self._create_event(client, alice_pet["id"], alice_headers)
        r = client.get(
            f"/pets/{alice_pet['id']}/events/{ev['id']}",
            headers=alice_headers,
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Vet visit"

    def test_event_not_found_returns_404(self, client, alice_headers, alice_pet):
        r = client.get(
            f"/pets/{alice_pet['id']}/events/{_UNKNOWN_ID}",
            headers=alice_headers,
        )
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_headers, alice_pet, bob_headers):
        ev = self._create_event(client, alice_pet["id"], alice_headers)
        r = client.get(
            f"/pets/{alice_pet['id']}/events/{ev['id']}",
            headers=bob_headers,
        )
        assert r.status_code == 403

    def test_invalid_event_uuid_returns_422(self, client, alice_headers, alice_pet):
        r = client.get(
            f"/pets/{alice_pet['id']}/events/{_BAD_UUID}",
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        r = client.get(f"/pets/{alice_pet['id']}/events/{_UNKNOWN_ID}")
        assert r.status_code == 401


class TestDeleteEvent:
    def _create_event(self, client, pet_id, headers):
        r = client.post(
            f"/pets/{pet_id}/events",
            json={"title": "Vet visit", "description": "All clear"},
            headers=headers,
        )
        return r.json()

    def test_success(self, client, alice_headers, alice_pet):
        ev = self._create_event(client, alice_pet["id"], alice_headers)
        r = client.delete(
            f"/pets/{alice_pet['id']}/events/{ev['id']}",
            headers=alice_headers,
        )
        assert r.status_code == 204

    def test_event_not_found_returns_404(self, client, alice_headers, alice_pet):
        r = client.delete(
            f"/pets/{alice_pet['id']}/events/{_UNKNOWN_ID}",
            headers=alice_headers,
        )
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_headers, alice_pet, bob_headers):
        ev = self._create_event(client, alice_pet["id"], alice_headers)
        r = client.delete(
            f"/pets/{alice_pet['id']}/events/{ev['id']}",
            headers=bob_headers,
        )
        assert r.status_code == 403

    def test_invalid_event_uuid_returns_422(self, client, alice_headers, alice_pet):
        r = client.delete(
            f"/pets/{alice_pet['id']}/events/{_BAD_UUID}",
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        r = client.delete(f"/pets/{alice_pet['id']}/events/{_UNKNOWN_ID}")
        assert r.status_code == 401
