from contextlib import asynccontextmanager

from fastapi import FastAPI

from identity.presentation.http.auth_router import router as auth_router
from petstore.infrastructure.persistence.database import initialise_schema
from petstore.presentation.http.pet_event_router import router as pet_event_router
from petstore.presentation.http.pet_router import router as pet_router

_DESCRIPTION = """
Pet Store API lets you register pets, track their life events, and share ownership
with other users — all protected by JWT Bearer authentication.

## Authentication

All `/pets` and `/events` endpoints require a Bearer token.

**Step 1 — create an account:**
```
POST /auth/register   { "username": "alice", "password": "s3cr3t" }
```

**Step 2 — use the returned `access_token` as a header on every request:**
```
Authorization: Bearer <access_token>
```

You can also exchange credentials for a token at any time via the standard
OAuth2 password flow:
```
POST /auth/token   (form data: username + password)
```

## Ownership model

* The user who registers a pet is its first owner.
* Any owner can add additional co-owners by username (`POST /pets/{id}/owners`).
* Any owner can remove another owner (`DELETE /pets/{id}/owners/{owner_id}`),
  but a pet must always retain **at least one owner**.
* Only owners can view, edit, or delete a pet and its events.
"""

_TAGS = [
    {
        "name": "auth",
        "description": "Register, log in, and inspect the current user. "
        "Tokens are JWT HS256, valid for 90 days.",
    },
    {
        "name": "pets",
        "description": "Create and manage pets. Every operation is scoped to the "
        "authenticated user's owned pets.",
    },
    {
        "name": "events",
        "description": "Record and retrieve timestamped life events for a pet "
        "(vet visits, vaccinations, grooming, etc.). "
        "Requires ownership of the parent pet.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialise_schema()
    yield


app = FastAPI(
    title="Pet Store API",
    version="2.0.0",
    description=_DESCRIPTION,
    openapi_tags=_TAGS,
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(pet_router)
app.include_router(pet_event_router)
