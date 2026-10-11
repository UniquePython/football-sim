from __future__ import annotations

from random import gauss
from typing import ClassVar

from .attributes import Attributes, BaseAttributes
from .development import (
    OFFSET_LIMIT,
    generate_development_offset,
    headroom_for,
)
from .faker import fakers
from .foot import MAX_WEAK_FOOT, MIN_WEAK_FOOT, Foot
from .generation import (
    TIERS,
    generate_attributes,
    generate_potential,
    generate_weak_foot,
)
from .growth import (
    class_levels,
    decline_attributes,
    expected_overall,
    grow_attributes,
    potential_from_current,
)
from .nationality import Nationality
from .position import Position
from .ratings import overall_rating
from .utils import require_condition, require_type, value_or_default
from .value import market_value, round_value


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
        potential: int | None = None,
        development_offset: float | None = None,
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

        if sum(arg is not None for arg in (overall, attributes, potential)) > 1:
            raise ValueError(
                "Pass at most one of overall, attributes or potential: "
                "each one already determines the others"
            )

        self._development_offset = require_condition(
            require_type(
                value_or_default(development_offset, generate_development_offset),
                float,
                "Player development offset must be of type float",
            ),
            lambda offset: -OFFSET_LIMIT <= offset <= OFFSET_LIMIT,
            f"Player development offset must be between {-OFFSET_LIMIT} and {OFFSET_LIMIT}",
        )

        if attributes is not None:
            self.attributes = require_type(
                attributes, Attributes, "Player attributes must be of type Attributes"
            )
            self._potential = self._potential_from_current_overall()
        elif overall is not None:
            overall = self._require_rating(overall, "overall")
            self._potential = potential_from_current(
                self.position, self.age, overall, self._development_offset
            )
            self.attributes = self._generate_attributes(overall)
        else:
            self._potential = self._require_rating(
                value_or_default(potential, generate_potential), "potential"
            )
            self.attributes = self._generate_attributes(
                expected_overall(
                    self.position, self.age, self._potential, self._development_offset
                )
            )

        self.weak_foot = value_or_default(
            weak_foot, lambda: generate_weak_foot(self.overall)
        )

        self.faker = fakers[self.nationality]
        self.first_name = self.faker.first_name_male()
        self.last_name = self.faker.last_name_male()

    @classmethod
    def _require_rating(cls, value: object, name: str) -> int:
        return require_condition(
            require_type(value, int, f"Player {name} must be of type int"),
            lambda rating: cls.MIN_OVERALL <= rating <= cls.MAX_OVERALL,
            f"Player {name} must be between {cls.MIN_OVERALL} and {cls.MAX_OVERALL}",
        )

    def _generate_attributes(self, target: int) -> Attributes:
        return generate_attributes(
            self.position,
            target,
            class_levels(
                self.position, self.age, self._potential, self._development_offset
            ),
        )

    def _potential_from_current_overall(self) -> int:
        return potential_from_current(
            self.position, self.age, self.overall, self._development_offset
        )

    def advance_year(self) -> None:
        if self.age >= self.MAX_AGE:
            raise ValueError(f"Player cannot be older than {self.MAX_AGE}")

        grown = grow_attributes(
            self.position,
            self.attributes,
            self.age,
            self._potential,
            self._development_offset,
        )
        self.attributes = decline_attributes(self.position, grown, self.age)
        self.age += 1

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
    def value(self) -> int:
        return round_value(market_value(self.overall, self.growth_headroom, self.age))

    @property
    def growth_headroom(self) -> int:
        return headroom_for(
            self.overall, self.potential, self.age, self._development_offset
        )

    @property
    def potential(self) -> int:
        return self._potential

    @property
    def development_offset(self) -> float:
        return self._development_offset

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
        return f"Player(nationality={self.nationality}, first_name={self.first_name!r}, last_name={self.last_name!r}, age={self.age}, position={self.position}, overall={self.overall}, potential={self.potential}, development_offset={self.development_offset:.2f}, attributes={self.attributes})"

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
            + f"\tOverall: {self.overall} (potential: {self.potential})\n"
            + f"\tValue: €{self.value:,}\n"
            + "\tAttributes:\n\t\t"
            + "\t\t".join(line + "\n" for line in str(self.attributes).split("\n"))
        )
