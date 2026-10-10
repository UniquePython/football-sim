from __future__ import annotations

from random import gauss
from typing import ClassVar

from .attributes import Attributes, BaseAttributes
from .faker import fakers
from .foot import MAX_WEAK_FOOT, MIN_WEAK_FOOT, Foot
from .generation import (
    TIERS,
    generate_attributes,
    generate_base_quality,
    generate_weak_foot,
)
from .nationality import Nationality
from .position import Position
from .ratings import overall_rating
from .utils import require_condition, require_type, value_or_default


class Player:
    MIN_AGE: ClassVar[int] = 16
    MAX_AGE: ClassVar[int] = 45
    MEAN_AGE: ClassVar[float] = 26.5
    AGE_STD_DEV: ClassVar[float] = 4.5
    MIN_OVERALL: ClassVar[int] = min(tier.low for tier in TIERS)
    MAX_OVERALL: ClassVar[int] = BaseAttributes.MAX

    def __init__(
        self,
        nationality: Nationality | None = None,
        age: int | None = None,
        position: Position | None = None,
        overall: int | None = None,
        attributes: Attributes | None = None,
        foot: Foot | None = None,
        weak_foot: int | None = None,
    ) -> None:
        self.nationality = require_type(
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

        if foot is not None:
            require_type(foot, Foot, "Player foot must be of type Foot")

        self.position = require_type(
            value_or_default(
                position,
                lambda: (
                    foot.random_position() if foot is not None else Position.random()
                ),
            ),
            Position,
            "Player position must be of type Position",
        )
        self._foot = value_or_default(foot, lambda: Foot.random_for(self.position))

        if overall is not None and attributes is not None:
            raise ValueError(
                "Pass either overall or attributes, not both: "
                "explicit attributes already determine the overall"
            )

        if attributes is not None:
            self.attributes = require_type(
                attributes, Attributes, "Player attributes must be of type Attributes"
            )
        else:
            target = require_condition(
                require_type(
                    value_or_default(overall, generate_base_quality),
                    int,
                    "Player overall must be of type int",
                ),
                lambda overall: self.MIN_OVERALL <= overall <= self.MAX_OVERALL,
                f"Player overall must be between {self.MIN_OVERALL} and {self.MAX_OVERALL}",
            )
            self.attributes = generate_attributes(self.position, target)

        self.weak_foot = value_or_default(
            weak_foot, lambda: generate_weak_foot(self.overall)
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
    def overall(self) -> int:
        return round(overall_rating(self.attributes, self.position))

    @property
    def foot(self) -> Foot:
        return self._foot

    @property
    def weak_foot(self) -> int:
        return self._weak_foot

    @weak_foot.setter
    def weak_foot(self, value: int) -> None:
        self._weak_foot = require_condition(
            require_type(value, int, "Player weak foot must be of type int"),
            lambda value: MIN_WEAK_FOOT <= value <= MAX_WEAK_FOOT,
            f"Player weak foot must be between {MIN_WEAK_FOOT} and {MAX_WEAK_FOOT}",
        )

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"Player(nationality={self.nationality}, first_name={self.first_name!r}, last_name={self.last_name!r}, age={self.age}, position={self.position}, overall={self.overall}, attributes={self.attributes})"

    def __str__(self) -> str:
        return (
            "Player:\n"
            + f"\tName: {self.name}\n"
            + f"\tCountry: {self.nationality.display_name}\n"
            + f"\tAge: {self.age}\n"
            + f"\tPosition: {self.position.abbreviation} ({self.position.group.value})\n"
            + f"\tFoot: {self.foot.value} (weak foot: "
            + "★" * self.weak_foot
            + ")\n"
            + f"\tOverall: {self.overall}\n"
            + "\tAttributes:\n\t\t"
            + "\t\t".join(line + "\n" for line in str(self.attributes).split("\n"))
        )
