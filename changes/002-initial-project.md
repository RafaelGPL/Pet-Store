# 002 — Initial Pet Store API

Created the pet-store-api project directory with the full DDD folder structure under a single petstore Bounded Context.
Wrote a project-level CLAUDE.md tailored to this codebase, listing the actual bounded context name, layer rules, and naming conventions.
Created the PetName Value Object as an immutable frozen dataclass that validates and normalises first and last name on construction.
Created the PetType Value Object as an immutable frozen dataclass that lowercases and validates the pet type on construction.
Created the OwnerName Value Object as an immutable frozen dataclass that strips whitespace and validates the owner name on construction.
Created the Pet Entity as the Aggregate Root with private state, property accessors, and behaviour methods: rename, change_type, and transfer_ownership.
Added two factory methods on Pet: register creates a new pet and raises a PetRegisteredEvent, reconstitute rehydrates a pet from the database without raising events.
Created the PetRegisteredEvent as an immutable domain event that captures the pet id, owner name, and UTC timestamp at the moment of creation.
Created PetNotFoundException and InvalidPetDataException in the domain exceptions module.
Created the IPetRepository interface in the domain layer with save, find_by_id, find_all, and delete methods, keeping the domain free of infrastructure concerns.
Created RegisterPetCommand, UpdatePetCommand, and DeletePetCommand as immutable frozen dataclasses in the application commands module.
Created GetPetQuery and ListPetsQuery as immutable frozen dataclasses in the application queries module.
Created PetDto as an immutable frozen dataclass with a from_pet static factory, ensuring domain objects never cross the application boundary.
Created RegisterPetHandler, UpdatePetHandler, DeletePetHandler, GetPetHandler, and ListPetsHandler, each accepting a repository interface and returning a DTO.
Implemented the SQLite schema initialisation in the infrastructure persistence module using the Python standard library sqlite3, with no ORM.
Implemented SqlitePetRepository with save using an upsert, find_by_id, find_all, and delete, translating rows back to domain objects via Pet.reconstitute.
Created Pydantic request and response models in the presentation layer: RegisterPetRequest, UpdatePetRequest, and PetResponse.
Created the FastAPI pet router with five endpoints: POST /pets, GET /pets, GET /pets/{id}, PATCH /pets/{id}, and DELETE /pets/{id}.
Wired everything together in main.py: schema initialisation on startup and router registration.
Added requirements.txt listing fastapi and uvicorn as the only two dependencies.
