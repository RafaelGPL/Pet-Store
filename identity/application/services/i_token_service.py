from abc import ABC, abstractmethod


class ITokenService(ABC):
    @abstractmethod
    def create_token(self, user_id: str) -> str: ...

    @abstractmethod
    def verify_token(self, token: str) -> str: ...
