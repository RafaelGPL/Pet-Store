"""
Pure unit tests for all domain objects — no HTTP, no database.
Covers every value-object validation branch, every entity method, and every
domain exception constructor.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------


class TestPetName:
    def test_valid(self):
        from petstore.domain.model.pet_name import PetName

        n = PetName(first="Tom", last="Phillips")
        assert n.first == "Tom"
        assert n.last == "Phillips"

    def test_strips_whitespace(self):
        from petstore.domain.model.pet_name import PetName

        n = PetName(first="  Tom  ", last="  Phillips  ")
        assert n.first == "Tom"
        assert n.last == "Phillips"

    def test_empty_first_raises(self):
        from petstore.domain.model.pet_name import PetName

        with pytest.raises(ValueError, match="first name"):
            PetName(first="", last="Phillips")

    def test_empty_last_raises(self):
        from petstore.domain.model.pet_name import PetName

        with pytest.raises(ValueError, match="last name"):
            PetName(first="Tom", last="")

    def test_full(self):
        from petstore.domain.model.pet_name import PetName

        assert PetName(first="Tom", last="Phillips").full() == "Tom Phillips"


class TestPetType:
    def test_valid_normalised_to_lowercase(self):
        from petstore.domain.model.pet_type import PetType

        t = PetType(value="CAT")
        assert t.value == "cat"

    def test_empty_raises(self):
        from petstore.domain.model.pet_type import PetType

        with pytest.raises(ValueError, match="cannot be empty"):
            PetType(value="")


class TestEventTitle:
    def test_valid(self):
        from petstore.domain.model.event_title import EventTitle

        assert EventTitle(value="Checkup").value == "Checkup"

    def test_empty_raises(self):
        from petstore.domain.model.event_title import EventTitle

        with pytest.raises(ValueError, match="cannot be empty"):
            EventTitle(value="   ")


class TestEventDescription:
    def test_valid(self):
        from petstore.domain.model.event_description import EventDescription

        assert EventDescription(value="All good").value == "All good"

    def test_empty_raises(self):
        from petstore.domain.model.event_description import EventDescription

        with pytest.raises(ValueError, match="cannot be empty"):
            EventDescription(value="")


class TestOwnerName:
    def test_valid(self):
        from petstore.domain.model.owner_name import OwnerName

        assert OwnerName(value="  Jenny  ").value == "Jenny"

    def test_empty_raises(self):
        from petstore.domain.model.owner_name import OwnerName

        with pytest.raises(ValueError, match="cannot be empty"):
            OwnerName(value="")


class TestUsername:
    def test_valid_normalised_to_lowercase(self):
        from identity.domain.model.username import Username

        u = Username(value="  Alice_01  ")
        assert u.value == "alice_01"

    def test_empty_raises(self):
        from identity.domain.model.username import Username

        with pytest.raises(ValueError, match="empty"):
            Username(value="   ")

    def test_too_short_raises(self):
        from identity.domain.model.username import Username

        with pytest.raises(ValueError, match="at least 3"):
            Username(value="ab")

    def test_too_long_raises(self):
        from identity.domain.model.username import Username

        with pytest.raises(ValueError, match="at most 50"):
            Username(value="a" * 51)

    def test_invalid_chars_raises(self):
        from identity.domain.model.username import Username

        with pytest.raises(ValueError, match="only contain"):
            Username(value="bad user!")


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------


class TestPet:
    def _make_pet(self):
        from petstore.domain.model.pet import Pet
        from petstore.domain.model.pet_name import PetName
        from petstore.domain.model.pet_type import PetType

        owner = uuid.uuid4()
        return (
            Pet.register(
                name=PetName(first="Whiskers", last="McFluff"),
                type_=PetType(value="cat"),
                initial_owner_id=owner,
            ),
            owner,
        )

    def test_register_creates_pet_and_event(self):
        pet, owner = self._make_pet()
        assert pet.name.first == "Whiskers"
        assert pet.type.value == "cat"
        assert owner in pet.owner_ids

    def test_pull_events_returns_and_clears(self):
        pet, _ = self._make_pet()
        events = pet.pull_events()
        assert len(events) == 1
        assert pet.pull_events() == []

    def test_reconstitute(self):
        from petstore.domain.model.pet import Pet
        from petstore.domain.model.pet_name import PetName
        from petstore.domain.model.pet_type import PetType

        pid = uuid.uuid4()
        oid = uuid.uuid4()
        pet = Pet.reconstitute(
            id=pid,
            name=PetName(first="Rex", last="Barker"),
            type_=PetType(value="dog"),
            owner_ids=[oid],
        )
        assert pet.id == pid
        assert pet.name.last == "Barker"

    def test_is_owned_by_true_and_false(self):
        pet, owner = self._make_pet()
        assert pet.is_owned_by(owner) is True
        assert pet.is_owned_by(uuid.uuid4()) is False

    def test_add_owner(self):
        pet, owner = self._make_pet()
        new_owner = uuid.uuid4()
        pet.add_owner(new_owner)
        assert new_owner in pet.owner_ids

    def test_remove_owner_success(self):
        pet, owner = self._make_pet()
        second = uuid.uuid4()
        pet.add_owner(second)
        pet.remove_owner(owner)
        assert owner not in pet.owner_ids

    def test_remove_last_owner_raises(self):
        from petstore.domain.exceptions.pet_exceptions import (
            PetMustHaveAtLeastOneOwnerException,
        )

        pet, owner = self._make_pet()
        with pytest.raises(PetMustHaveAtLeastOneOwnerException):
            pet.remove_owner(owner)

    def test_rename(self):
        from petstore.domain.model.pet_name import PetName

        pet, _ = self._make_pet()
        pet.rename(PetName(first="Shadow", last="Night"))
        assert pet.name.first == "Shadow"

    def test_change_type(self):
        from petstore.domain.model.pet_type import PetType

        pet, _ = self._make_pet()
        pet.change_type(PetType(value="tiger"))
        assert pet.type.value == "tiger"


class TestPetEvent:
    def test_record(self):
        from petstore.domain.model.event_description import EventDescription
        from petstore.domain.model.event_title import EventTitle
        from petstore.domain.model.pet_event import PetEvent

        pid = uuid.uuid4()
        ev = PetEvent.record(
            pet_id=pid,
            title=EventTitle(value="Checkup"),
            description=EventDescription(value="All good"),
        )
        assert ev.pet_id == pid
        assert ev.title.value == "Checkup"
        assert ev.description.value == "All good"
        assert isinstance(ev.occurred_at, datetime)

    def test_reconstitute(self):
        from petstore.domain.model.event_description import EventDescription
        from petstore.domain.model.event_title import EventTitle
        from petstore.domain.model.pet_event import PetEvent

        eid = uuid.uuid4()
        pid = uuid.uuid4()
        ts = datetime.now(timezone.utc)
        ev = PetEvent.reconstitute(
            id=eid,
            pet_id=pid,
            title=EventTitle(value="Checkup"),
            description=EventDescription(value="All good"),
            occurred_at=ts,
        )
        assert ev.id == eid
        assert ev.occurred_at == ts


class TestPetRegisteredEvent:
    def test_creation(self):
        from petstore.domain.events.pet_registered_event import PetRegisteredEvent

        pid = uuid.uuid4()
        oid = uuid.uuid4()
        ev = PetRegisteredEvent(pet_id=pid, owner_id=oid)
        assert ev.pet_id == pid
        assert ev.owner_id == oid
        assert isinstance(ev.occurred_at, datetime)


class TestUser:
    def test_register(self):
        from identity.domain.model.user import User
        from identity.domain.model.username import Username

        u = User.register(username=Username(value="alice"), password_hash="hash")
        assert u.username.value == "alice"
        assert u.password_hash == "hash"
        assert isinstance(u.id, uuid.UUID)

    def test_reconstitute(self):
        from identity.domain.model.user import User
        from identity.domain.model.username import Username

        uid = uuid.uuid4()
        u = User.reconstitute(id=uid, username=Username(value="bob"), password_hash="h")
        assert u.id == uid


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class TestPetExceptions:
    def test_pet_not_found(self):
        from petstore.domain.exceptions.pet_exceptions import PetNotFoundException

        pid = uuid.uuid4()
        exc = PetNotFoundException(pid)
        assert str(pid) in str(exc)

    def test_pet_event_not_found(self):
        from petstore.domain.exceptions.pet_exceptions import PetEventNotFoundException

        eid = uuid.uuid4()
        exc = PetEventNotFoundException(eid)
        assert str(eid) in str(exc)

    def test_pet_access_denied(self):
        from petstore.domain.exceptions.pet_exceptions import PetAccessDeniedException

        pid = uuid.uuid4()
        exc = PetAccessDeniedException(pid)
        assert str(pid) in str(exc)

    def test_pet_must_have_at_least_one_owner(self):
        from petstore.domain.exceptions.pet_exceptions import (
            PetMustHaveAtLeastOneOwnerException,
        )

        pid = uuid.uuid4()
        exc = PetMustHaveAtLeastOneOwnerException(pid)
        assert str(pid) in str(exc)

    def test_invalid_pet_data(self):
        from petstore.domain.exceptions.pet_exceptions import InvalidPetDataException

        exc = InvalidPetDataException("bad")
        assert exc is not None


class TestUserExceptions:
    def test_user_already_exists(self):
        from identity.domain.exceptions.user_exceptions import UserAlreadyExistsException

        exc = UserAlreadyExistsException("alice")
        assert "alice" in str(exc)

    def test_user_not_found(self):
        from identity.domain.exceptions.user_exceptions import UserNotFoundException

        exc = UserNotFoundException("alice")
        assert "alice" in str(exc)

    def test_invalid_credentials(self):
        from identity.domain.exceptions.user_exceptions import InvalidCredentialsException

        exc = InvalidCredentialsException()
        assert exc is not None

    def test_invalid_token(self):
        from identity.domain.exceptions.user_exceptions import InvalidTokenException

        exc = InvalidTokenException()
        assert exc is not None


# ---------------------------------------------------------------------------
# JWT token service edge cases
# ---------------------------------------------------------------------------


class TestJwtTokenService:
    def test_create_and_verify(self):
        from identity.infrastructure.security.jwt_token_service import JwtTokenService

        svc = JwtTokenService()
        uid = str(uuid.uuid4())
        token = svc.create_token(uid)
        assert svc.verify_token(token) == uid

    def test_invalid_token_raises(self):
        from identity.domain.exceptions.user_exceptions import InvalidTokenException
        from identity.infrastructure.security.jwt_token_service import JwtTokenService

        svc = JwtTokenService()
        with pytest.raises(InvalidTokenException):
            svc.verify_token("not.a.valid.token")

    def test_token_without_sub_raises(self):
        """A structurally valid JWT that has no 'sub' claim must be rejected."""
        from identity.domain.exceptions.user_exceptions import InvalidTokenException
        from identity.infrastructure.security.jwt_token_service import (
            ALGORITHM,
            SECRET_KEY,
            JwtTokenService,
        )

        token_no_sub = jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        svc = JwtTokenService()
        with pytest.raises(InvalidTokenException):
            svc.verify_token(token_no_sub)
