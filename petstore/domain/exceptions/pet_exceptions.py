import uuid


class PetNotFoundException(Exception):
    def __init__(self, pet_id: uuid.UUID) -> None:
        super().__init__(f"Pet '{pet_id}' not found")
        self.pet_id = pet_id


class PetEventNotFoundException(Exception):
    def __init__(self, event_id: uuid.UUID) -> None:
        super().__init__(f"Event '{event_id}' not found")
        self.event_id = event_id


class PetAccessDeniedException(Exception):
    def __init__(self, pet_id: uuid.UUID) -> None:
        super().__init__(f"Access denied to pet '{pet_id}'")
        self.pet_id = pet_id


class PetMustHaveAtLeastOneOwnerException(Exception):
    def __init__(self, pet_id: uuid.UUID) -> None:
        super().__init__(f"Pet '{pet_id}' must retain at least one owner")
        self.pet_id = pet_id


class InvalidPetDataException(Exception):
    pass
