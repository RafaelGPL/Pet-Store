from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticateUserQuery:
    username: str
    password: str
