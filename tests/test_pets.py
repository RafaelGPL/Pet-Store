"""Tests for /pets/* endpoints — CRUD, ownership management, and access control."""

import uuid


_UNKNOWN_ID = str(uuid.uuid4())
_BAD_UUID = "not-a-uuid"


class TestRegisterPet:
    def test_success(self, client, alice_headers, alice):
        r = client.post(
            "/pets",
            json={"name": "Whiskers", "last_name": "McFluff", "type": "cat"},
            headers=alice_headers,
        )
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "Whiskers"
        assert alice["user_id"] in body["owner_ids"]

    def test_no_token_returns_401(self, client):
        r = client.post("/pets", json={"name": "X", "last_name": "Y", "type": "cat"})
        assert r.status_code == 401

    def test_whitespace_name_returns_422(self, client, alice_headers):
        r = client.post(
            "/pets",
            json={"name": " ", "last_name": "Y", "type": "cat"},
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_whitespace_type_returns_422(self, client, alice_headers):
        r = client.post(
            "/pets",
            json={"name": "X", "last_name": "Y", "type": "  "},
            headers=alice_headers,
        )
        assert r.status_code == 422


class TestListPets:
    def test_empty_list(self, client, alice_headers):
        r = client.get("/pets", headers=alice_headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_owned_pets_only(self, client, alice_headers, bob_headers):
        client.post(
            "/pets",
            json={"name": "A", "last_name": "A", "type": "cat"},
            headers=alice_headers,
        )
        client.post(
            "/pets",
            json={"name": "B", "last_name": "B", "type": "dog"},
            headers=bob_headers,
        )
        r = client.get("/pets", headers=alice_headers)
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_no_token_returns_401(self, client):
        assert client.get("/pets").status_code == 401


class TestGetPet:
    def test_success(self, client, alice_headers, alice_pet):
        r = client.get(f"/pets/{alice_pet['id']}", headers=alice_headers)
        assert r.status_code == 200
        assert r.json()["id"] == alice_pet["id"]

    def test_not_found_returns_404(self, client, alice_headers):
        r = client.get(f"/pets/{_UNKNOWN_ID}", headers=alice_headers)
        assert r.status_code == 404

    def test_other_users_pet_returns_403(self, client, alice_pet, bob_headers):
        r = client.get(f"/pets/{alice_pet['id']}", headers=bob_headers)
        assert r.status_code == 403

    def test_invalid_uuid_returns_422(self, client, alice_headers):
        r = client.get(f"/pets/{_BAD_UUID}", headers=alice_headers)
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        assert client.get(f"/pets/{alice_pet['id']}").status_code == 401


class TestUpdatePet:
    def test_update_name_only(self, client, alice_headers, alice_pet):
        r = client.patch(
            f"/pets/{alice_pet['id']}",
            json={"name": "Shadow"},
            headers=alice_headers,
        )
        assert r.status_code == 200
        assert r.json()["name"] == "Shadow"
        assert r.json()["last_name"] == alice_pet["last_name"]

    def test_update_last_name_only(self, client, alice_headers, alice_pet):
        r = client.patch(
            f"/pets/{alice_pet['id']}",
            json={"last_name": "Nightpaw"},
            headers=alice_headers,
        )
        assert r.status_code == 200
        assert r.json()["last_name"] == "Nightpaw"
        assert r.json()["name"] == alice_pet["name"]

    def test_update_type_only(self, client, alice_headers, alice_pet):
        r = client.patch(
            f"/pets/{alice_pet['id']}",
            json={"type": "tiger"},
            headers=alice_headers,
        )
        assert r.status_code == 200
        assert r.json()["type"] == "tiger"

    def test_update_all_fields(self, client, alice_headers, alice_pet):
        r = client.patch(
            f"/pets/{alice_pet['id']}",
            json={"name": "Rex", "last_name": "Barker", "type": "dog"},
            headers=alice_headers,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "Rex"
        assert body["last_name"] == "Barker"
        assert body["type"] == "dog"

    def test_update_no_fields_is_no_op(self, client, alice_headers, alice_pet):
        r = client.patch(f"/pets/{alice_pet['id']}", json={}, headers=alice_headers)
        assert r.status_code == 200
        assert r.json()["name"] == alice_pet["name"]

    def test_not_found_returns_404(self, client, alice_headers):
        r = client.patch(f"/pets/{_UNKNOWN_ID}", json={"name": "X"}, headers=alice_headers)
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_pet, bob_headers):
        r = client.patch(
            f"/pets/{alice_pet['id']}", json={"name": "X"}, headers=bob_headers
        )
        assert r.status_code == 403

    def test_blank_name_returns_422(self, client, alice_headers, alice_pet):
        r = client.patch(
            f"/pets/{alice_pet['id']}",
            json={"name": " "},
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_invalid_uuid_returns_422(self, client, alice_headers):
        r = client.patch(f"/pets/{_BAD_UUID}", json={"name": "X"}, headers=alice_headers)
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        assert client.patch(f"/pets/{alice_pet['id']}", json={}).status_code == 401


class TestDeletePet:
    def test_success(self, client, alice_headers, alice_pet):
        r = client.delete(f"/pets/{alice_pet['id']}", headers=alice_headers)
        assert r.status_code == 204

    def test_not_found_returns_404(self, client, alice_headers):
        r = client.delete(f"/pets/{_UNKNOWN_ID}", headers=alice_headers)
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_pet, bob_headers):
        r = client.delete(f"/pets/{alice_pet['id']}", headers=bob_headers)
        assert r.status_code == 403

    def test_invalid_uuid_returns_422(self, client, alice_headers):
        r = client.delete(f"/pets/{_BAD_UUID}", headers=alice_headers)
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        assert client.delete(f"/pets/{alice_pet['id']}").status_code == 401


class TestAddOwner:
    def test_success(self, client, alice_headers, alice_pet, bob, alice, bob_headers):
        r = client.post(
            f"/pets/{alice_pet['id']}/owners",
            json={"username": "bob"},
            headers=alice_headers,
        )
        assert r.status_code == 200
        assert bob["user_id"] in r.json()["owner_ids"]
        assert alice["user_id"] in r.json()["owner_ids"]

    def test_pet_not_found_returns_404(self, client, alice_headers):
        r = client.post(
            f"/pets/{_UNKNOWN_ID}/owners",
            json={"username": "someone"},
            headers=alice_headers,
        )
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_pet, bob_headers):
        r = client.post(
            f"/pets/{alice_pet['id']}/owners",
            json={"username": "someone"},
            headers=bob_headers,
        )
        assert r.status_code == 403

    def test_target_user_not_found_returns_404(self, client, alice_headers, alice_pet):
        r = client.post(
            f"/pets/{alice_pet['id']}/owners",
            json={"username": "nobody"},
            headers=alice_headers,
        )
        assert r.status_code == 404

    def test_invalid_uuid_returns_422(self, client, alice_headers):
        r = client.post(
            f"/pets/{_BAD_UUID}/owners",
            json={"username": "bob"},
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet):
        r = client.post(f"/pets/{alice_pet['id']}/owners", json={"username": "bob"})
        assert r.status_code == 401


class TestRemoveOwner:
    def test_success(self, client, alice_headers, alice_pet, bob, alice):
        # First add bob
        client.post(
            f"/pets/{alice_pet['id']}/owners",
            json={"username": "bob"},
            headers=alice_headers,
        )
        # Alice removes herself
        r = client.delete(
            f"/pets/{alice_pet['id']}/owners/{alice['user_id']}",
            headers=alice_headers,
        )
        assert r.status_code == 200
        assert alice["user_id"] not in r.json()["owner_ids"]

    def test_pet_not_found_returns_404(self, client, alice_headers):
        r = client.delete(
            f"/pets/{_UNKNOWN_ID}/owners/{_UNKNOWN_ID}",
            headers=alice_headers,
        )
        assert r.status_code == 404

    def test_forbidden_returns_403(self, client, alice_pet, bob_headers, alice):
        r = client.delete(
            f"/pets/{alice_pet['id']}/owners/{alice['user_id']}",
            headers=bob_headers,
        )
        assert r.status_code == 403

    def test_last_owner_returns_409(self, client, alice_headers, alice_pet, alice):
        r = client.delete(
            f"/pets/{alice_pet['id']}/owners/{alice['user_id']}",
            headers=alice_headers,
        )
        assert r.status_code == 409

    def test_invalid_pet_uuid_returns_422(self, client, alice_headers):
        r = client.delete(
            f"/pets/{_BAD_UUID}/owners/{_UNKNOWN_ID}",
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_invalid_owner_uuid_returns_422(self, client, alice_headers, alice_pet):
        r = client.delete(
            f"/pets/{alice_pet['id']}/owners/{_BAD_UUID}",
            headers=alice_headers,
        )
        assert r.status_code == 422

    def test_no_token_returns_401(self, client, alice_pet, alice):
        r = client.delete(f"/pets/{alice_pet['id']}/owners/{alice['user_id']}")
        assert r.status_code == 401
