import uuid

from identity.domain.model.username import Username


class User:
    def __init__(
        self,
        id: uuid.UUID,
        username: Username,
        password_hash: str,
    ) -> None:
        self._id = id
        self._username = username
        self._password_hash = password_hash

    # --- factories ---

    @classmethod
    def register(cls, username: Username, password_hash: str) -> "User":
        return cls(id=uuid.uuid4(), username=username, password_hash=password_hash)

    @classmethod
    def reconstitute(cls, id: uuid.UUID, username: Username, password_hash: str) -> "User":
        return cls(id=id, username=username, password_hash=password_hash)

    # --- properties ---

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def username(self) -> Username:
        return self._username

    @property
    def password_hash(self) -> str:
        return self._password_hash
