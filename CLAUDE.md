# Architecture: Domain-Driven Design (DDD)

This project follows **Domain-Driven Design**. All code structure, naming, and organisation must reflect the domain model, not technical concerns.

## Bounded Context

This project has a single Bounded Context: **petstore**.

## Folder Structure

```
petstore/
  domain/
    model/          # Entities, Value Objects, Aggregates
    events/         # Domain Events
    repositories/   # Repository interfaces (contracts only — no implementations)
    exceptions/     # Domain-specific exceptions
  application/
    commands/       # Command objects (write-side use cases)
    queries/        # Query objects (read-side use cases)
    handlers/       # Command and Query handlers
    dto/            # Data Transfer Objects (cross-boundary output)
  infrastructure/
    persistence/    # Repository implementations, raw SQLite3
  presentation/
    http/           # FastAPI routers and Pydantic request/response models
main.py
```

## Domain Model

| Class | Type | Rule |
|---|---|---|
| `Pet` | Entity / Aggregate Root | Identity via UUID; state only changes through its own methods |
| `PetName` | Value Object | Immutable frozen dataclass; validates non-empty first + last |
| `PetType` | Value Object | Immutable frozen dataclass; normalises to lowercase |
| `OwnerName` | Value Object | Immutable frozen dataclass; validates non-empty |
| `PetRegisteredEvent` | Domain Event | Raised by `Pet.register()`; immutable; past tense |
| `IPetRepository` | Repository interface | Lives in domain; no infrastructure imports |

## Layer Rules

1. **Domain** — zero dependencies on FastAPI, SQLite, or any framework.
2. **Application** — orchestrates domain objects; no business logic; returns `PetDto`, never `Pet`.
3. **Infrastructure** — implements `IPetRepository`; translates rows → `Pet.reconstitute()`; maps infra exceptions to domain exceptions.
4. **Presentation** — FastAPI routers only; Pydantic models (`*Request`, `*Response`) live here and nowhere else; catches domain exceptions, maps to HTTP status codes.

## Naming Conventions

| Concept | Pattern | Example |
|---|---|---|
| Entity | Noun, no suffix | `Pet` |
| Value Object | Noun phrase, no suffix | `PetName`, `OwnerName` |
| Repository interface | `I<Entity>Repository` | `IPetRepository` |
| Repository impl | `<Store><Entity>Repository` | `SqlitePetRepository` |
| Command | Imperative verb phrase + `Command` | `RegisterPetCommand` |
| Query | Noun phrase + `Query` | `GetPetQuery` |
| Handler | `<Command|Query>Handler` | `RegisterPetHandler` |
| Domain Event | Past-tense + `Event` | `PetRegisteredEvent` |
| DTO | Noun + `Dto` | `PetDto` |

## Key Constraints

- **No anemic model.** `Pet` exposes `rename()`, `change_type()`, `transfer_ownership()` — never public setters.
- **Reconstitute vs register.** Loading from DB uses `Pet.reconstitute()` (no events). Creating new uses `Pet.register()` (raises `PetRegisteredEvent`).
- **No ORM annotations on domain objects.** SQLite mapping lives entirely in `SqlitePetRepository._to_pet()`.
- **Ubiquitous language.** Use domain terms in all code, commits, and comments: `register`, `rename`, `transfer_ownership`.

---

## Git Workflow: Git-Flow

This project uses **Git-Flow** as its branching and release convention. Always follow these rules when performing any git operation.

### Branch Structure

| Branch | Purpose |
|---|---|
| `main` | Always reflects production-ready code. Only receives merges from `release/*` and `hotfix/*` branches. |
| `develop` | Integration branch. All completed features merge here first. |
| `feature/*` | New features. Branch from `develop`, merge back to `develop` when complete. |
| `release/*` | Release preparation (version bumps, final fixes). Branch from `develop`, merge to both `main` and `develop`. |
| `hotfix/*` | Urgent production fixes. Branch from `main`, merge to both `main` and `develop`. |

### Branch Naming

- Features: `feature/<short-description>` — e.g. `feature/pet-vaccination-records`
- Releases: `release/<version>` — e.g. `release/1.2.0`
- Hotfixes: `hotfix/<short-description>` — e.g. `hotfix/fix-event-404`

### Commit Message Rules

- Use imperative mood: "Add", "Fix", "Update", "Remove", "Refactor"
- Keep the subject line under 72 characters
- Use the body to explain *why*, not *what*

### Hard Rules

- Never commit directly to `main`.
- Never commit directly to `develop` for anything larger than a trivial single-line fix.
- Every feature, release, and hotfix must go through its own named branch.
- `main` and `develop` must always be in a passing, runnable state.
- Before creating a new branch, always confirm you are branching from the correct base (`develop` for features, `main` for hotfixes).

### Code Style

All Python files are automatically formatted by **black** via a pre-commit hook. Never skip the pre-commit hook. If black reformats a file, review the diff before pushing.
