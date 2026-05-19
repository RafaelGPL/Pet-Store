import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from petstore.domain.model.pet_event import PetEvent


class IPetEventRepository(ABC):
    @abstractmethod
    def save(self, event: PetEvent) -> None: ...

    @abstractmethod
    def find_by_id(self, event_id: uuid.UUID) -> Optional[PetEvent]: ...

    @abstractmethod
    def find_by_pet_id(self, pet_id: uuid.UUID) -> List[PetEvent]: ...

    @abstractmethod
    def delete(self, event_id: uuid.UUID) -> None: ...
