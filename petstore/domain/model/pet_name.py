from dataclasses import dataclass


@dataclass(frozen=True)
class PetName:
    first: str
    last: str

    def __post_init__(self) -> None:
        first = self.first.strip()
        last = self.last.strip()
        if not first:
            raise ValueError("Pet first name cannot be empty")
        if not last:
            raise ValueError("Pet last name cannot be empty")
        object.__setattr__(self, "first", first)
        object.__setattr__(self, "last", last)

    def full(self) -> str:
        return f"{self.first} {self.last}"
