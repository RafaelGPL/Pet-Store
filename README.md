```
 ██████╗ ███████╗████████╗    ███████╗████████╗ ██████╗ ██████╗ ███████╗
 ██╔══██╗██╔════╝╚══██╔══╝    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
 ██████╔╝█████╗     ██║       ███████╗   ██║   ██║   ██║██████╔╝█████╗
 ██╔═══╝ ██╔══╝     ██║       ╚════██║   ██║   ██║   ██║██╔══██╗██╔══╝
 ██║     ███████╗   ██║       ███████║   ██║   ╚██████╔╝██║  ██║███████╗
 ╚═╝     ╚══════╝   ╚═╝       ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
```
<div align="center">

**🐾 Not a pet shop. A pet archive. 🐾**

*REST API for storing, tracking, and managing your beloved companions and their life events.*

---

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen?style=flat-square)
![Architecture](https://img.shields.io/badge/Architecture-DDD-blueviolet?style=flat-square)
![Code Style](https://img.shields.io/badge/Code%20Style-black-000000?style=flat-square)
![Git Flow](https://img.shields.io/badge/Git-Flow-F05032?style=flat-square&logo=git&logoColor=white)

</div>

---

## 🐶🐱🐦 What is this?

**Pet Store** is a RESTful API for archiving pets and their life events — think of it as a personal record keeper for every furry, scaly, or feathered companion in your life. Register pets with their name, type, and owners, then attach a running timeline of events to each one: vet visits, vaccinations, grooming sessions, milestones, whatever matters.

It is **not** a pet shop. Nobody is for sale here.

Built with **FastAPI** and **SQLite3**, following strict **Domain-Driven Design (DDD)** across two Bounded Contexts — every file, folder, class, and object reflects the domain, not the framework.

---

## ✨ Features

- **JWT authentication** — register, log in, and receive a Bearer token; all pet and event endpoints are protected
- Register pets with name, type, and multiple owners
- Retrieve, update, and remove pet records (owners only)
- **Shared ownership** — add or remove co-owners on any pet; a pet must always have at least one owner
- Attach timestamped life events to any pet (vet visits, vaccinations, milestones…)
- List and retrieve the full event history per pet
- Input validation with meaningful error messages on every endpoint
- Zero external database dependencies — SQLite3 ships with Python
- **100% statement and branch coverage** enforced on every pull request via GitHub Actions
- Auto-formatted code via `black` on every commit

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| ASGI server | Uvicorn |
| Database | SQLite3 (stdlib) |
| Authentication | JWT (python-jose + passlib/bcrypt) |
| Architecture | Domain-Driven Design (DDD) |
| Testing | pytest + pytest-cov |
| Code style | black |
| CI | GitHub Actions |
| Python | 3.8+ |

---

## 📁 Project Structure

```
pet-store-api/
├── main.py                          # App entry point — lifespan, schema init, router wiring
├── requirements.txt
├── pytest.ini                       # Test runner config — coverage flags, test path
├── .coveragerc                      # Coverage config — branch=true, fail_under=100
├── CLAUDE.md                        # DDD + Git-Flow rules for this project
│
├── .github/
│   └── workflows/
│       └── coverage.yml             # CI: runs full test suite + enforces 100% coverage on PRs
│
├── tests/                           # Full test suite (120 tests)
│   ├── conftest.py                  # Shared fixtures — isolated DB, fast bcrypt, test client
│   ├── test_auth.py                 # /auth/* endpoint tests
│   ├── test_pets.py                 # /pets/* endpoint tests
│   ├── test_events.py               # /pets/{id}/events/* endpoint tests
│   └── test_domain.py               # Pure unit tests — domain model, value objects, exceptions
│
├── identity/                        # Bounded Context: user identity + authentication
│   ├── domain/
│   │   ├── model/                   # User entity, Username value object
│   │   ├── repositories/            # IUserRepository interface
│   │   ├── services/                # IPasswordService, ITokenService interfaces
│   │   └── exceptions/              # UserAlreadyExistsException, InvalidCredentialsException…
│   ├── application/
│   │   ├── commands/                # RegisterUserCommand, AuthenticateUserCommand
│   │   ├── handlers/                # RegisterUserHandler, AuthenticateUserHandler
│   │   └── dto/                     # UserDto, TokenDto
│   ├── infrastructure/
│   │   ├── persistence/             # SqliteUserRepository
│   │   └── security/                # BcryptPasswordService, JwtTokenService
│   └── presentation/
│       └── http/                    # auth_router — /auth/register, /auth/token, /auth/me
│
└── petstore/                        # Bounded Context: pets and their life events
    ├── domain/
    │   ├── model/                   # Pet aggregate, PetEvent entity, value objects
    │   ├── events/                  # PetRegisteredEvent
    │   ├── repositories/            # IPetRepository, IPetEventRepository interfaces
    │   └── exceptions/              # PetNotFoundException, PetAccessDeniedException…
    ├── application/
    │   ├── commands/                # RegisterPetCommand, AddPetEventCommand…
    │   ├── queries/                 # GetPetQuery, ListPetsQuery…
    │   ├── handlers/                # One handler per command or query
    │   └── dto/                     # PetDto, PetEventDto
    ├── infrastructure/
    │   └── persistence/             # SqlitePetRepository, SqlitePetEventRepository
    └── presentation/
        └── http/                    # pet_router, pet_event_router
```

---

## 🌐 API Endpoints

Base URL: `http://localhost:8000`

Interactive docs (Swagger UI): [`http://localhost:8000/docs`](http://localhost:8000/docs)

All `/pets` and `/pets/{id}/events` endpoints require a **Bearer token** in the `Authorization` header. Obtain one via `/auth/register` or `/auth/token`.

---

### Authentication

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| `POST` | `/auth/register` | Create a new user account and receive a token | No |
| `POST` | `/auth/token` | Log in with credentials and receive a token | No |
| `GET` | `/auth/me` | Return the currently authenticated user | Yes |

**Register / login request**

`POST /auth/register` accepts JSON; `POST /auth/token` accepts `application/x-www-form-urlencoded` (OAuth2 standard).

```json
{ "username": "alice", "password": "supersecret" }
```

**Token response**
```json
{
  "user_id":      "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username":     "alice",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type":   "bearer"
}
```

Username rules: 3–50 characters, letters/digits/underscores/hyphens only.

---

### Pets

All endpoints require authentication. Results are scoped to the authenticated user — you only see pets you own.

| Method | Endpoint | Description | Request Body | Success |
|---|---|---|---|---|
| `POST` | `/pets` | Register a new pet | `RegisterPetRequest` | `201 Created` |
| `GET` | `/pets` | List your pets | — | `200 OK` |
| `GET` | `/pets/{id}` | Get a pet by ID | — | `200 OK` |
| `PATCH` | `/pets/{id}` | Update one or more pet fields | `UpdatePetRequest` | `200 OK` |
| `DELETE` | `/pets/{id}` | Remove a pet | — | `204 No Content` |
| `POST` | `/pets/{id}/owners` | Add a co-owner by username | `{"username": "bob"}` | `200 OK` |
| `DELETE` | `/pets/{id}/owners/{user_id}` | Remove an owner | — | `200 OK` |

**`RegisterPetRequest`**
```json
{
  "name":      "Whiskers",
  "last_name": "McFluff",
  "type":      "cat"
}
```

**`UpdatePetRequest`** — all fields optional
```json
{
  "name":      "Shadow",
  "last_name": "Nightpaw",
  "type":      "panther"
}
```

**`PetResponse`**
```json
{
  "id":        "507e5993-dcc4-4641-8a58-b3ba9d58f26b",
  "name":      "Whiskers",
  "last_name": "McFluff",
  "type":      "cat",
  "owner_ids": ["3fa85f64-5717-4562-b3fc-2c963f66afa6"]
}
```

Ownership rules:
- The user who registers a pet is automatically its first owner.
- Any existing owner can add another user as a co-owner via `POST /pets/{id}/owners`.
- Any existing owner can remove themselves or other owners, **but a pet must always have at least one owner** — removing the last owner returns `409 Conflict`.

---

### Pet Events

Events are timestamped records attached to a pet. Only the pet's owners can create, read, or delete events.

| Method | Endpoint | Description | Request Body | Success |
|---|---|---|---|---|
| `POST` | `/pets/{pet_id}/events` | Add an event to a pet | `AddPetEventRequest` | `201 Created` |
| `GET` | `/pets/{pet_id}/events` | List all events for a pet | — | `200 OK` |
| `GET` | `/pets/{pet_id}/events/{event_id}` | Get a specific event | — | `200 OK` |
| `DELETE` | `/pets/{pet_id}/events/{event_id}` | Remove an event | — | `204 No Content` |

**`AddPetEventRequest`**
```json
{
  "title":       "Annual checkup",
  "description": "Routine annual wellness exam. All vitals normal."
}
```

**`PetEventResponse`**
```json
{
  "id":          "a0c8b8f5-38e8-4180-8dbe-d3be01b2aa4b",
  "pet_id":      "507e5993-dcc4-4641-8a58-b3ba9d58f26b",
  "title":       "Annual checkup",
  "description": "Routine annual wellness exam. All vitals normal.",
  "occurred_at": "2026-05-18T23:34:39.167963+00:00"
}
```

---

### Error Responses

| Status | When |
|---|---|
| `401 Unauthorized` | Missing or invalid Bearer token |
| `403 Forbidden` | Token is valid but the user does not own the pet |
| `404 Not Found` | Pet, event, or user ID does not exist |
| `409 Conflict` | Attempt to remove the last owner of a pet |
| `422 Unprocessable Entity` | Validation failure (e.g. blank name, invalid UUID, short username) |

---

## 🧪 Testing

The project has **120 tests** and enforces **100% statement and branch coverage**.

```bash
# Run the full suite with coverage report
pytest

# Run a specific test file
pytest tests/test_auth.py -v
```

Coverage is measured across both bounded contexts. Every domain branch — including error paths, access-control checks, and edge cases — has a dedicated test.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **pip** (comes with Python)
- No database setup required — SQLite3 is part of the Python standard library

---

### 🪟 Windows

> **Recommended:** run inside [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) (Ubuntu) for the best experience. If you don't have WSL, the native instructions below work too.

**Option A — WSL2 (recommended)**

Open your WSL terminal and follow the Linux instructions below.

**Option B — Native Windows (PowerShell)**

```powershell
# 1. Clone the project
cd C:\path\to\pet-store-api

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> If `uvicorn` is not found after install, use:
> ```powershell
> python -m uvicorn main:app --reload
> ```

---

### 🍎 macOS

```bash
# 1. Clone the project
cd /path/to/pet-store-api

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> macOS ships with Python 2 on older versions. Make sure `python3 --version` returns 3.8+.
> Install a newer Python via [Homebrew](https://brew.sh): `brew install python`.

---

### 🐧 Linux

```bash
# 1. Clone the project
cd /path/to/pet-store-api

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> If `uvicorn` lands in `~/.local/bin` and is not on your PATH, run it as:
> ```bash
> python3 -m uvicorn main:app --reload
> ```

---

### ✅ Verify it's running

Once the server is up you should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Open [`http://localhost:8000/docs`](http://localhost:8000/docs) for the interactive Swagger UI, or [`http://localhost:8000/redoc`](http://localhost:8000/redoc) for the ReDoc view.

---

## 📦 Dependencies

### Runtime

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥ 0.111.0 | Web framework and request validation |
| `uvicorn[standard]` | ≥ 0.29.0 | ASGI server |
| `python-jose[cryptography]` | ≥ 3.3.0 | JWT creation and verification |
| `passlib[bcrypt]` | ≥ 1.7.4 | Password hashing |
| `bcrypt` | ≥ 3.2.0, < 4.0.0 | bcrypt backend (pinned for passlib compatibility) |
| `python-multipart` | ≥ 0.0.9 | OAuth2 form-data parsing (`/auth/token`) |

### Testing

| Package | Version | Purpose |
|---|---|---|
| `pytest` | ≥ 8.0.0 | Test runner |
| `pytest-cov` | ≥ 5.0.0 | Coverage measurement and enforcement |
| `httpx` | ≥ 0.27.0 | In-process HTTP client for `TestClient` |

### Development

| Package | Version | Purpose |
|---|---|---|
| `black` | ≥ 24.0.0 | Code formatter — runs automatically on every commit via pre-commit hook |

> `sqlite3` is part of the Python standard library and requires no installation.

Install everything at once:

```bash
pip install -r requirements.txt
```

---

## ⚙️ CI / GitHub Actions

Every pull request to `main` triggers the `Tests & 100% coverage` workflow (`.github/workflows/coverage.yml`):

1. Checks out the code
2. Sets up Python 3.11 with pip caching
3. Installs dependencies
4. Runs `pytest` — which reads `pytest.ini` and enforces `--cov-fail-under=100`

**The check is required** — GitHub branch protection blocks merging if it fails or if coverage drops below 100%.

---

## 🔀 Git Workflow

This project follows **Git-Flow**:

```
main        ← production-ready only; never commit here directly
 └── develop ← integration branch; all features merge here
      └── feature/<name>    ← branch from develop, merge back to develop
      └── release/<version> ← branch from develop, merge to main + develop
      └── hotfix/<name>     ← branch from main, merge to main + develop
```

PRs to `main` use **rebase merge** — no merge commits, linear history.

Starting a new feature:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature
# ... do work ...
# open a PR targeting develop
```

---

## 🏛️ Architecture

The project is built on **Domain-Driven Design (DDD)** with two Bounded Contexts:

**`identity`** — everything about users: registration, authentication, JWT issuance, and password verification. The Pet Store knows about user IDs but never imports from `identity` directly.

**`petstore`** — everything about pets and their events: ownership, lifecycle, event recording. References users by ID only.

Each context follows the same internal layering:

- **Domain** — pure Python; zero framework dependencies; all business rules and invariants live here
- **Application** — orchestrates domain objects; one handler per use case; returns DTOs, never domain objects
- **Infrastructure** — SQLite3 repository implementations; the domain model has no knowledge of storage
- **Presentation** — FastAPI routers; Pydantic request/response models; maps domain exceptions to HTTP status codes

See [`CLAUDE.md`](CLAUDE.md) for the full architecture reference and Git-Flow rules.

---

<div align="center">
Made with 🐾 and way too much attention to folder structure.
</div>
