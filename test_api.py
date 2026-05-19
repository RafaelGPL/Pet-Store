"""
Pet Store API — smoke tests for multi-owner + OAuth2 flow.

Run after the server is up:
    python3 test_api.py
"""

import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"

errors = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def req(method, path, body=None, token=None, form=False):
    url = BASE + path
    data = None
    headers = {}
    if body is not None:
        if form:
            data = urllib.parse.urlencode(body).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw) if raw else {}


def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS}  {label}")
    else:
        print(f"  {FAIL}  {label}" + (f" — {detail}" if detail else ""))
        errors.append(label)


def section(title):
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

section("Register users")

status_code, alice = req("POST", "/auth/register", {"username": "alice", "password": "s3cr3tA!"})
check("Alice registers (201)", status_code == 201, status_code)
alice_token = alice.get("access_token", "")
alice_id = alice.get("user_id", "")
check("Alice token returned", bool(alice_token))

status_code, bob = req("POST", "/auth/register", {"username": "bob", "password": "s3cr3tB!"})
check("Bob registers (201)", status_code == 201, status_code)
bob_token = bob.get("access_token", "")
bob_id = bob.get("user_id", "")
check("Bob token returned", bool(bob_token))

status_code, _ = req("POST", "/auth/register", {"username": "alice", "password": "other"})
check("Duplicate username rejected (409)", status_code == 409, status_code)

section("Login via OAuth2 token endpoint")

status_code, login = req(
    "POST", "/auth/token", {"username": "alice", "password": "s3cr3tA!"}, form=True
)
check("Alice can log in (200)", status_code == 200, status_code)
check("Login returns bearer token type", login.get("token_type") == "bearer")

status_code, _ = req(
    "POST", "/auth/token", {"username": "alice", "password": "wrong"}, form=True
)
check("Bad password rejected (401)", status_code == 401, status_code)

section("GET /auth/me")

status_code, me = req("GET", "/auth/me", token=alice_token)
check("Alice can see herself (200)", status_code == 200, status_code)
check("Me returns correct username", me.get("username") == "alice", me.get("username"))

status_code, _ = req("GET", "/auth/me")
check("Unauthenticated /me rejected (401)", status_code == 401, status_code)

# ---------------------------------------------------------------------------
# Pets — ownership isolation
# ---------------------------------------------------------------------------

section("Register pets")

status_code, pet_a = req(
    "POST",
    "/pets",
    {"name": "Whiskers", "last_name": "McFluff", "type": "cat"},
    token=alice_token,
)
check("Alice registers pet (201)", status_code == 201, status_code)
pet_a_id = pet_a.get("id", "")
check("Pet belongs to Alice", alice_id in pet_a.get("owner_ids", []))

status_code, pet_b = req(
    "POST",
    "/pets",
    {"name": "Rex", "last_name": "Barker", "type": "dog"},
    token=bob_token,
)
check("Bob registers pet (201)", status_code == 201, status_code)
pet_b_id = pet_b.get("id", "")
check("Bob's pet belongs to Bob", bob_id in pet_b.get("owner_ids", []))

section("Ownership isolation")

status_code, pets = req("GET", "/pets", token=alice_token)
check(
    "Alice only sees her own pet",
    status_code == 200 and len(pets) == 1 and pets[0]["id"] == pet_a_id,
    pets,
)

status_code, _ = req("GET", f"/pets/{pet_a_id}", token=bob_token)
check("Bob cannot see Alice's pet (403)", status_code == 403, status_code)

status_code, _ = req("PATCH", f"/pets/{pet_a_id}", {"name": "Shadow"}, token=bob_token)
check("Bob cannot rename Alice's pet (403)", status_code == 403, status_code)

status_code, _ = req("DELETE", f"/pets/{pet_a_id}", token=bob_token)
check("Bob cannot delete Alice's pet (403)", status_code == 403, status_code)

# ---------------------------------------------------------------------------
# Co-ownership
# ---------------------------------------------------------------------------

section("Co-ownership — add owner")

status_code, updated = req(
    "POST", f"/pets/{pet_a_id}/owners", {"username": "bob"}, token=alice_token
)
check("Alice adds Bob as co-owner (200)", status_code == 200, status_code)
owner_ids = updated.get("owner_ids", [])
check(
    "Both IDs in owner_ids",
    alice_id in owner_ids and bob_id in owner_ids,
    owner_ids,
)

status_code, _ = req("GET", f"/pets/{pet_a_id}", token=bob_token)
check("Bob can now access the shared pet (200)", status_code == 200, status_code)

status_code, bobs_pets = req("GET", "/pets", token=bob_token)
ids = [p["id"] for p in bobs_pets]
check("Bob's list includes shared pet", pet_a_id in ids, ids)

section("Co-ownership — remove owner")

status_code, after_remove = req(
    "DELETE", f"/pets/{pet_a_id}/owners/{alice_id}", token=alice_token
)
check("Alice removes herself (200)", status_code == 200, status_code)

status_code, now_bobs = req("GET", f"/pets/{pet_a_id}", token=bob_token)
check("Bob still owns the pet after Alice leaves (200)", status_code == 200, status_code)
remaining = set(now_bobs.get("owner_ids", []))
check("Only Bob remains as owner", remaining == {bob_id}, remaining)

status_code, _ = req("GET", f"/pets/{pet_a_id}", token=alice_token)
check("Alice can no longer access the pet (403)", status_code == 403, status_code)

section("Last-owner guard")

status_code, _ = req("DELETE", f"/pets/{pet_a_id}/owners/{bob_id}", token=bob_token)
check("Cannot remove last owner (409)", status_code == 409, status_code)

# ---------------------------------------------------------------------------
# Pet events (using Bob's pet)
# ---------------------------------------------------------------------------

section("Pet events — authenticated CRUD")

status_code, ev = req(
    "POST",
    f"/pets/{pet_b_id}/events",
    {"title": "Vet check-up", "description": "Annual vaccination done."},
    token=bob_token,
)
check("Bob adds event to his pet (201)", status_code == 201, status_code)
ev_id = ev.get("id", "")
check("Event tied to correct pet", ev.get("pet_id") == pet_b_id)

status_code, evs = req("GET", f"/pets/{pet_b_id}/events", token=bob_token)
check("Bob lists events (200)", status_code == 200 and len(evs) >= 1)

status_code, got_ev = req("GET", f"/pets/{pet_b_id}/events/{ev_id}", token=bob_token)
check("Bob fetches single event (200)", status_code == 200)
check("Event title correct", got_ev.get("title") == "Vet check-up", got_ev.get("title"))

section("Event access control")

status_code, _ = req("GET", f"/pets/{pet_b_id}/events/{ev_id}", token=alice_token)
check("Alice cannot read Bob's event (403)", status_code == 403, status_code)

status_code, _ = req(
    "POST",
    f"/pets/{pet_b_id}/events",
    {"title": "Sneaky event", "description": "Should be blocked."},
    token=alice_token,
)
check("Alice cannot add event to Bob's pet (403)", status_code == 403, status_code)

status_code, _ = req("DELETE", f"/pets/{pet_b_id}/events/{ev_id}", token=alice_token)
check("Alice cannot delete Bob's event (403)", status_code == 403, status_code)

status_code, _ = req("DELETE", f"/pets/{pet_b_id}/events/{ev_id}", token=bob_token)
check("Bob deletes his event (204)", status_code == 204, status_code)

status_code, evs_after = req("GET", f"/pets/{pet_b_id}/events", token=bob_token)
check("Events list empty after deletion", status_code == 200 and len(evs_after) == 0, evs_after)

section("Validation")

status_code, _ = req(
    "POST",
    f"/pets/{pet_b_id}/events",
    {"title": "", "description": "Empty title"},
    token=bob_token,
)
check("Empty event title rejected (422)", status_code == 422, status_code)

status_code, _ = req(
    "GET",
    "/pets/00000000-0000-0000-0000-000000000000/events",
    token=alice_token,
)
check("Events for non-existent pet gives 404", status_code == 404, status_code)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print(f"\n{'═' * 55}")
if errors:
    print(f"  {FAIL}  {len(errors)} test(s) failed:")
    for e in errors:
        print(f"        • {e}")
else:
    print(f"  {PASS}  All tests passed!")
print(f"{'═' * 55}\n")

raise SystemExit(1 if errors else 0)
