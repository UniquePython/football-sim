from __future__ import annotations

from random import choice

from .faker import fakers
from .nationality import Nationality
from .utils import require_type_and_not_none


class Player:
    def __init__(self, nationality: Nationality) -> None:
        self.nationality = require_type_and_not_none(nationality, Nationality)
        self.faker = fakers[self.nationality]
        self.first_name = self.faker.first_name_male()
        self.last_name = self.faker.last_name_male()

    @classmethod
    def random(cls) -> Player:
        nationality = choice(list(Nationality))
        return cls(nationality)

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"Player(nationality={self.nationality}, first_name={self.first_name!r}, last_name={self.last_name!r})"

    def __str__(self) -> str:
        return f"Player {self.name} from {self.nationality.display_name}"
