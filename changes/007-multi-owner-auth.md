## 007 — Multi-Owner Pets + OAuth2 Authentication

### Summary
Pets can now be co-owned by multiple registered users. All API endpoints are protected by JWT Bearer tokens issued via OAuth2. User data is fully private — each user can only see and modify pets they own.

---

### Steps taken

1. Added a new `identity` bounded context alongside the existing `petstore` context, covering user registration, login, and token management.

2. Created `identity/domain/model/username.py` — a self-validating Value Object that normalises usernames to lowercase and enforces 3–50 character, alphanumeric rules.

3. Created `identity/domain/model/user.py` — a `User` entity with `register()` (new user, raises event) and `reconstitute()` (load from DB) factory methods.

4. Created `identity/domain/exceptions/user_exceptions.py` — domain exceptions: `UserAlreadyExistsException`, `UserNotFoundException`, `InvalidCredentialsException`, `InvalidTokenException`.

5. Created `identity/domain/repositories/i_user_repository.py` — repository interface with `save`, `find_by_id`, and `find_by_username` contracts.

6. Created `identity/application/services/i_password_service.py` and `i_token_service.py` — abstract interfaces keeping bcrypt and JWT details out of the application layer.

7. Created `identity/application/handlers/register_user_handler.py` — orchestrates username validation, uniqueness check, password hashing, user persistence, and token generation.

8. Created `identity/application/handlers/authenticate_user_handler.py` — verifies credentials and issues a new JWT.

9. Created `identity/application/handlers/get_current_user_handler.py` — loads the user matching the token's subject claim.

10. Created `identity/infrastructure/security/bcrypt_password_service.py` — implements `IPasswordService` using `passlib[bcrypt]`.

11. Created `identity/infrastructure/security/jwt_token_service.py` — implements `ITokenService` using `python-jose[cryptography]`; tokens expire after 90 days; secret key read from `JWT_SECRET_KEY` environment variable (falls back to a dev default).

12. Created `identity/infrastructure/persistence/sqlite_user_repository.py` — stores users in the shared SQLite database. Reuses `get_connection` from the petstore persistence module (acknowledged monolith tradeoff; separate databases would apply in a distributed deployment).

13. Created `identity/presentation/http/dependencies.py` — `get_current_user_id()` FastAPI dependency that validates the Bearer token and returns the user's UUID string.

14. Created `identity/presentation/http/auth_router.py` — three endpoints: `POST /auth/register`, `POST /auth/token` (OAuth2 password flow), and `GET /auth/me`.

15. Rewrote `petstore/domain/model/pet.py` — replaced single `owner` string with `owner_ids: Set[uuid.UUID]`; added `add_owner()`, `remove_owner()` (enforces at-least-one invariant), and `is_owned_by()` methods.

16. Updated `petstore/domain/exceptions/pet_exceptions.py` — added `PetAccessDeniedException` and `PetMustHaveAtLeastOneOwnerException`.

17. Updated `petstore/domain/repositories/i_pet_repository.py` — replaced `find_all()` with `find_by_owner(user_id)`.

18. Updated all petstore application commands to carry `requesting_user_id`; added new `AddPetOwnerCommand` and `RemovePetOwnerCommand`.

19. Updated all petstore application queries to carry `requesting_user_id`.

20. Rewrote all petstore application handlers to check `pet.is_owned_by(requesting_user_id)` and raise `PetAccessDeniedException` on mismatch.

21. Added `AddPetOwnerHandler` — looks up the new owner by username via `IUserRepository`, then calls `pet.add_owner()`.

22. Added `RemovePetOwnerHandler` — calls `pet.remove_owner()`, which enforces the last-owner invariant.

23. Updated `petstore/infrastructure/persistence/database.py` — replaced the `owner` column on `pets` with a new `pet_owners` join table; added `users` table; enabled `PRAGMA foreign_keys = ON`.

24. Rewrote `petstore/infrastructure/persistence/sqlite_pet_repository.py` — `save()` upserts pet rows and re-syncs the `pet_owners` join table; `find_by_id()` loads owner IDs via a secondary query; `find_by_owner()` joins `pets` with `pet_owners` to return only pets visible to the requesting user.

25. Rewrote `petstore/presentation/http/pet_router.py` — all routes require a Bearer token via `Depends(get_current_user_id)`; `PetResponse` returns `owner_ids` instead of `owner`; added `POST /pets/{id}/owners` (add co-owner by username) and `DELETE /pets/{id}/owners/{owner_id}` (remove co-owner).

26. Rewrote `petstore/presentation/http/pet_event_router.py` — all routes require a Bearer token; handlers now receive `requesting_user_id` so access is checked against pet ownership.

27. Updated `main.py` — registered the `auth_router` and bumped the API version to `2.0.0`.

28. Updated `requirements.txt` — added `python-jose[cryptography]>=3.3.0` and `passlib[bcrypt]>=1.7.4`.

29. Rewrote `test_api.py` — full end-to-end suite: two users register and log in, pet isolation is verified, co-ownership add/remove is exercised, last-owner guard is tested, and event access control is confirmed.
