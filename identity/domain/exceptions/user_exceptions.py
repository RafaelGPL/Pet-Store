class UserAlreadyExistsException(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f"User '{username}' already exists")
        self.username = username


class UserNotFoundException(Exception):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"User '{identifier}' not found")
        self.identifier = identifier


class InvalidCredentialsException(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid username or password")


class InvalidTokenException(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid or expired token")
