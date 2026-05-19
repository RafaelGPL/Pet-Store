from dataclasses import dataclass


@dataclass(frozen=True)
class EventDescription:
    value: str

    def __post_init__(self) -> None:
        stripped = self.value.strip()
        if not stripped:
            raise ValueError("Event description cannot be empty")
        object.__setattr__(self, "value", stripped)
