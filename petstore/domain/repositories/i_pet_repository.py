import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from petstore.domain.model.pet import Pet


class IPetRepository(ABC):
    @abstractmethod
    def save(self, pet: Pet) -> None: ...

    @abstractmethod
    def find_by_id(self, pet_id: uuid.UUID) -> Optional[Pet]: ...

    @abstractmethod
    def find_by_owner(self, user_id: uuid.UUID) -> List[Pet]: ...

    @abstractmethod
    def delete(self, pet_id: uuid.UUID) -> None: ...
