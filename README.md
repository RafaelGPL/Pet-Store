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
![Architecture](https://img.shields.io/badge/Architecture-DDD-blueviolet?style=flat-square)
![Code Style](https://img.shields.io/badge/Code%20Style-black-000000?style=flat-square)
![Git Flow](https://img.shields.io/badge/Git-Flow-F05032?style=flat-square&logo=git&logoColor=white)

</div>

---

## 🐶🐱🐦 What is this?

**Pet Store** is a RESTful API for archiving pets and their life events — think of it as a personal record keeper for every furry, scaly, or feathered companion in your life. Register pets with their name, type, and owner, then attach a running timeline of events to each one: vet visits, vaccinations, grooming sessions, milestones, whatever matters.

It is **not** a pet shop. Nobody is for sale here.

Built with **FastAPI** and **SQLite3**, following strict **Domain-Driven Design (DDD)** — every file, folder, class, and object reflects the domain, not the framework.

---

## ✨ Features

- Register pets with name, type, and owner
- Retrieve, update, and remove pet records
- Attach timestamped life events to any pet (vet visits, vaccinations, milestones…)
- List and retrieve the full event history per pet
- Input validation with meaningful error messages
- Zero external database dependencies — SQLite3 ships with Python
- Auto-formatted code via `black` on every commit

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| ASGI server | Uvicorn |
| Database | SQLite3 (stdlib) |
| Architecture | Domain-Driven Design (DDD) |
| Code style | black |
| Python | 3.8+ |

---

## 📁 Project Structure

```
pet-store-api/
├── main.py                          # App entry point — wires schema + routers
├── requirements.txt
├── CLAUDE.md                        # DDD + Git-Flow rules for this project
├── changes/                         # Human-readable change log per milestone
│
└── petstore/                        # Single Bounded Context
    ├── domain/
    │   ├── model/                   # Entities, Value Objects, Aggregates
    │   ├── events/                  # Domain Events
    │   ├── repositories/            # Repository interfaces (contracts only)
    │   └── exceptions/              # Domain-specific exceptions
    ├── application/
    │   ├── commands/                # Write-side use case inputs
    │   ├── queries/                 # Read-side use case inputs
    │   ├── handlers/                # One handler per command or query
    │   └── dto/                     # Data Transfer Objects (boundary output)
    ├── infrastructure/
    │   └── persistence/             # SQLite3 repository implementations
    └── presentation/
        └── http/                    # FastAPI routers + Pydantic request/response models
```

---

## 🌐 API Endpoints

Base URL: `http://localhost:8000`

Interactive docs (Swagger UI): [`http://localhost:8000/docs`](http://localhost:8000/docs)

### Pets

| Method | Endpoint | Description | Request Body | Success |
|---|---|---|---|---|
| `POST` | `/pets` | Register a new pet | `RegisterPetRequest` | `201 Created` |
| `GET` | `/pets` | List all pets | — | `200 OK` |
| `GET` | `/pets/{id}` | Get a pet by ID | — | `200 OK` |
| `PATCH` | `/pets/{id}` | Update one or more pet fields | `UpdatePetRequest` | `200 OK` |
| `DELETE` | `/pets/{id}` | Remove a pet | — | `204 No Content` |

**`RegisterPetRequest`**
```json
{
  "name":      "Tom",
  "last_name": "Phillips",
  "type":      "cat",
  "owner":     "Jenny Jennyson"
}
```

**`UpdatePetRequest`** — all fields optional
```json
{
  "name":      "Tommy",
  "last_name": "Phillips",
  "type":      "cat",
  "owner":     "Carlos Reyes"
}
```

**`PetResponse`**
```json
{
  "id":        "507e5993-dcc4-4641-8a58-b3ba9d58f26b",
  "name":      "Tom",
  "last_name": "Phillips",
  "type":      "cat",
  "owner":     "Jenny Jennyson"
}
```

---

### Pet Events

Events are timestamped records attached to a pet — vet visits, vaccinations, milestones, anything worth remembering.

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
| `404 Not Found` | Pet or event ID does not exist |
| `422 Unprocessable Entity` | Validation failure (e.g. empty name, blank title) |

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
# 1. Clone or copy the project
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
# 1. Clone or copy the project
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
# 1. Clone or copy the project
cd /path/to/pet-store-api

# 2. (Optional but recommended) Create a virtual environment
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

Open [`http://localhost:8000/docs`](http://localhost:8000/docs) in your browser for the interactive Swagger UI.

---

## 📦 Dependencies

### Runtime

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥ 0.111.0 | Web framework and request validation |
| `uvicorn[standard]` | ≥ 0.29.0 | ASGI server |

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

## 🔀 Git Workflow

This project follows **Git-Flow**:

```
main        ← production-ready only; never commit here directly
 └── develop ← integration branch; all features merge here
      └── feature/<name>   ← branch from develop, merge back to develop
      └── release/<version> ← branch from develop, merge to main + develop
      └── hotfix/<name>    ← branch from main, merge to main + develop
```

Starting a new feature:

```bash
git checkout develop
git checkout -b feature/my-new-feature
# ... do work ...
git checkout develop
git merge --no-ff feature/my-new-feature
```

---

## 🏛️ Architecture

The project is built on **Domain-Driven Design (DDD)**. Code is organised by domain concern, not by technical layer:

- **Domain** — pure Python; zero framework dependencies; all business rules live here
- **Application** — orchestrates domain objects; one handler per use case; never exposes domain objects across its boundary
- **Infrastructure** — SQLite3 repository implementations; the domain model has no knowledge of storage
- **Presentation** — FastAPI routers; Pydantic request/response models; maps domain exceptions to HTTP status codes

See [`CLAUDE.md`](CLAUDE.md) for the full architecture reference and Git-Flow rules.

---

<div align="center">
Made with 🐾 and way too much attention to folder structure.
</div>
