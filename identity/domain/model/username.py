from dataclasses import dataclass


@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip().lower()
        if not stripped:
            raise ValueError("Username cannot be empty")
        if len(stripped) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(stripped) > 50:
            raise ValueError("Username must be at most 50 characters")
        if not stripped.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, hyphens, and underscores")
        object.__setattr__(self, "value", stripped)
