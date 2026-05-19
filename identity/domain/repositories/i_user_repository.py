import uuid
from abc import ABC, abstractmethod
from typing import Optional

from identity.domain.model.user import User


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]: ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]: ...
