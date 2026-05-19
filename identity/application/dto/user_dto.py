from dataclasses import dataclass

from identity.domain.model.user import User


@dataclass(frozen=True)
class UserDto:
    id: str
    username: str
    access_token: str = ""

    @staticmethod
    def from_user(user: User, access_token: str = "") -> "UserDto":
        return UserDto(
            id=str(user.id),
            username=user.username.value,
            access_token=access_token,
        )
