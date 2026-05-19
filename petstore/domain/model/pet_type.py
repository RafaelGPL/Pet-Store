from dataclasses import dataclass


@dataclass(frozen=True)
class PetType:
    value: str

    def __post_init__(self) -> None:
        normalised = self.value.strip().lower()
        if not normalised:
            raise ValueError("Pet type cannot be empty")
        object.__setattr__(self, "value", normalised)
