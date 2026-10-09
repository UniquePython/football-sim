from __future__ import annotations

from random import gauss
from typing import ClassVar

from .faker import fakers
from .nationality import Nationality
from .position import Position
from .utils import require_condition, require_type, value_or_default


class Player:
    MIN_AGE: ClassVar[int] = 16
    MAX_AGE: ClassVar[int] = 45
    MEAN_AGE: ClassVar[float] = 26.5
    AGE_STD_DEV: ClassVar[float] = 4.5

    def __init__(
        self,
        nationality: Nationality | None = None,
        age: int | None = None,
        position: Position | None = None,
    ) -> None:
        self.nationality = self.nationality = require_type(
            value_or_default(nationality, Nationality.random),
            Nationality,
            "Player nationality must be of type Nationality",
        )
        self.age = require_condition(
            require_type(
                value_or_default(age, type(self)._generate_age),
                int,
                "Player age must be of type int",
            ),
            lambda age: self.MIN_AGE <= age <= self.MAX_AGE,
            f"Player age must be between {self.MIN_AGE} and {self.MAX_AGE}",
        )

        self.position = require_type(
            value_or_default(position, Position.random),
            Position,
            "Player position must be of type Position",
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

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"Player(nationality={self.nationality}, first_name={self.first_name!r}, last_name={self.last_name!r}, age={self.age}, position={self.position})"

    def __str__(self) -> str:
        return (
            "Player:\n"
            + f"\tName: {self.name}\n"
            + f"\tCountry: {self.nationality.display_name}\n"
            + f"\tAge: {self.age}\n"
            + f"\tPosition: {self.position.abbreviation} ({self.position.group.value})\n"
        )
