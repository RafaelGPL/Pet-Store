from dataclasses import dataclass


@dataclass(frozen=True)
class OwnerName:
    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("Owner name cannot be empty")
        object.__setattr__(self, "value", stripped)
