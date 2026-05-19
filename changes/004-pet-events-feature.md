# 004 — Pet Events Feature

Decided to model PetEvent as its own Aggregate Root separate from Pet, referencing Pet by pet_id UUID only, following the DDD rule that cross-aggregate references must use identifiers not object references.
Created the EventTitle Value Object as an immutable frozen dataclass that strips whitespace and validates the title is non-empty.
Created the EventDescription Value Object as an immutable frozen dataclass that strips whitespace and validates the description is non-empty.
Created the PetEvent Entity with private state and property accessors for id, pet_id, title, description, and occurred_at.
Added two factory methods on PetEvent: record creates a new event and automatically sets occurred_at to the current UTC time, reconstitute rehydrates an event from the database without side effects.
Created the IPetEventRepository interface in the domain layer with save, find_by_id, find_by_pet_id, and delete methods.
Added PetEventNotFoundException to the domain exceptions module alongside the existing PetNotFoundException.
Created AddPetEventCommand and DeletePetEventCommand as immutable frozen dataclasses in the application commands module.
Created ListPetEventsQuery and GetPetEventQuery as immutable frozen dataclasses in the application queries module.
Created PetEventDto as an immutable frozen dataclass with a from_pet_event static factory, serialising occurred_at as an ISO 8601 string.
Created AddPetEventHandler, which accepts both IPetRepository and IPetEventRepository so it can verify the pet exists before recording the event.
Created ListPetEventsHandler, GetPetEventHandler, and DeletePetEventHandler, each accepting only IPetEventRepository.
Added the pet_events table to the SQLite schema in database.py with a foreign key referencing the pets table.
Implemented SqlitePetEventRepository with save using an upsert, find_by_id, find_by_pet_id ordered by occurred_at ascending, and delete.
Created Pydantic request and response models in the presentation layer: AddPetEventRequest and PetEventResponse.
Created the FastAPI pet event router with four endpoints: POST /pets/{pet_id}/events, GET /pets/{pet_id}/events, GET /pets/{pet_id}/events/{event_id}, and DELETE /pets/{pet_id}/events/{event_id}.
Registered the new router in main.py alongside the existing pet router.
Synced all changes to WSL using rsync and restarted the server with a clean database.
Ran eleven smoke test assertions covering: add events to two pets, list per pet, fetch single event, delete event, confirm deletion via 404, add event to unknown pet returns 404, and empty title returns 422.
All eleven assertions passed against the live server running on WSL Ubuntu.
