import uuid
from typing import List, Set

from petstore.domain.model.pet_name import PetName
from petstore.domain.model.pet_type import PetType


class Pet:
    def __init__(
        self,
        id: uuid.UUID,
        name: PetName,
        type_: PetType,
        owner_ids: List[uuid.UUID],
    ) -> None:
        self._id = id
        self._name = name
        self._type = type_
        self._owner_ids: Set[uuid.UUID] = set(owner_ids)
        self._events: list = []

    # --- factories ---

    @classmethod
    def register(
        cls,
        name: PetName,
        type_: PetType,
        initial_owner_id: uuid.UUID,
    ) -> "Pet":
        from petstore.domain.events.pet_registered_event import PetRegisteredEvent

        pet = cls(id=uuid.uuid4(), name=name, type_=type_, owner_ids=[initial_owner_id])
        pet._events.append(PetRegisteredEvent(pet_id=pet.id, owner_id=initial_owner_id))
        return pet

    @classmethod
    def reconstitute(
        cls,
        id: uuid.UUID,
        name: PetName,
        type_: PetType,
        owner_ids: List[uuid.UUID],
    ) -> "Pet":
        return cls(id=id, name=name, type_=type_, owner_ids=owner_ids)

    # --- properties ---

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def name(self) -> PetName:
        return self._name

    @property
    def type(self) -> PetType:
        return self._type

    @property
    def owner_ids(self) -> List[uuid.UUID]:
        return list(self._owner_ids)

    # --- ownership behaviour ---

    def is_owned_by(self, user_id: uuid.UUID) -> bool:
        return user_id in self._owner_ids

    def add_owner(self, user_id: uuid.UUID) -> None:
        self._owner_ids.add(user_id)

    def remove_owner(self, user_id: uuid.UUID) -> None:
        from petstore.domain.exceptions.pet_exceptions import PetMustHaveAtLeastOneOwnerException

        if len(self._owner_ids) <= 1:
            raise PetMustHaveAtLeastOneOwnerException(self._id)
        self._owner_ids.discard(user_id)

    # --- other behaviour ---

    def rename(self, new_name: PetName) -> None:
        self._name = new_name

    def change_type(self, new_type: PetType) -> None:
        self._type = new_type

    def pull_events(self) -> List:
        events = list(self._events)
        self._events.clear()
        return events
