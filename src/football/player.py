from __future__ import annotations

from random import choice, gauss
from typing import ClassVar

from .faker import fakers
from .nationality import Nationality
from .utils import require_condition, require_type_and_not_none


class Player:
    MIN_AGE: ClassVar[int] = 16
    MAX_AGE: ClassVar[int] = 45
    MEAN_AGE: ClassVar[float] = 26.5
    AGE_STD_DEV: ClassVar[float] = 4.5

    def __init__(self, nationality: Nationality, age: int) -> None:
        self.nationality = require_type_and_not_none(
            nationality,
            Nationality,
            "Player nationality must be of type Nationality",
            "Player nationality cannot be None",
        )
        self.age = require_condition(
            require_type_and_not_none(
                age,
                int,
                "Player age must be of type int",
                "Player age cannot be None",
            ),
            lambda age: self.MIN_AGE <= age <= self.MAX_AGE,
            f"Player age must be between {self.MIN_AGE} and {self.MAX_AGE}",
        )

        self.faker = fakers[self.nationality]
        self.first_name = self.faker.first_name_male()
        self.last_name = self.faker.last_name_male()

    @classmethod
    def _generate_age(cls) -> int:
        while True:
            age = round(gauss(cls.MEAN_AGE, cls.AGE_STD_DEV))
            if cls.MIN_AGE <= age <= cls.MAX_AGE:
                return age

    @classmethod
    def random(cls) -> Player:
        nationality = choice(list(Nationality))
        age = cls._generate_age()
        return cls(nationality, age)

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"Player(nationality={self.nationality}, first_name={self.first_name!r}, last_name={self.last_name!r}, age={self.age})"

    def __str__(self) -> str:
        return f"Player {self.name} from {self.nationality.display_name} is {self.age} years old"
