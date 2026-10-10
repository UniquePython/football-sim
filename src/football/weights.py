from dataclasses import dataclass, field, fields
from typing import ClassVar

from .attributes import Attributes
from .utils import require_condition, require_type_and_not_none


class BaseWeights:
    MIN: ClassVar[int] = 0
    MAX: ClassVar[int] = 10

    def __post_init__(self) -> None:
        for f in fields(self):  # type: ignore[arg-type]
            name = f.name
            value = getattr(self, name)

            require_condition(
                require_type_and_not_none(
                    value,
                    int,
                    f"Weight {name} must be of type int",
                    f"Weight {name} must not be None",
                ),
                lambda value: self.MIN <= value <= self.MAX,
                f"Weight {name} must be between {self.MIN} and {self.MAX}",
            )

    @property
    def total(self) -> int:
        return sum(getattr(self, f.name) for f in fields(self))  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class DribblingWeights(BaseWeights):
    agility: int = 0
    balance: int = 0
    ball_control: int = 0
    dribbling: int = 0


@dataclass(frozen=True, slots=True)
class ShootingWeights(BaseWeights):
    positioning: int = 0
    finishing: int = 0
    shot_power: int = 0
    long_shots: int = 0


@dataclass(frozen=True, slots=True)
class PassingWeights(BaseWeights):
    vision: int = 0
    crossing: int = 0
    short_passing: int = 0
    long_passing: int = 0
    curve: int = 0


@dataclass(frozen=True, slots=True)
class DefendingWeights(BaseWeights):
    positioning: int = 0
    interceptions: int = 0
    heading: int = 0
    standing_tackling: int = 0
    slide_tackling: int = 0


@dataclass(frozen=True, slots=True)
class PaceWeights(BaseWeights):
    acceleration: int = 0
    sprint_speed: int = 0


@dataclass(frozen=True, slots=True)
class PhysicalWeights(BaseWeights):
    jumping: int = 0
    strength: int = 0
    stamina: int = 0


@dataclass(frozen=True, slots=True)
class GoalKeepingWeights(BaseWeights):
    positioning: int = 0
    diving: int = 0
    handling: int = 0
    reflexes: int = 0


@dataclass(frozen=True, slots=True)
class Weights:
    dribbling: DribblingWeights = field(default_factory=DribblingWeights)
    shooting: ShootingWeights = field(default_factory=ShootingWeights)
    passing: PassingWeights = field(default_factory=PassingWeights)
    defending: DefendingWeights = field(default_factory=DefendingWeights)
    pace: PaceWeights = field(default_factory=PaceWeights)
    physical: PhysicalWeights = field(default_factory=PhysicalWeights)
    goalkeeping: GoalKeepingWeights = field(default_factory=GoalKeepingWeights)

    def __post_init__(self) -> None:
        require_condition(
            self.total, lambda total: total > 0, "Weights must have at least one point"
        )

    @property
    def total(self) -> int:
        return sum(getattr(self, f.name).total for f in fields(self))

    def overall(self, attributes: Attributes) -> float:
        weighted_sum = 0

        for group in fields(self):
            weights = getattr(self, group.name)
            values = getattr(attributes, group.name)

            for attribute in fields(weights):
                weighted_sum += getattr(values, attribute.name) * getattr(
                    weights, attribute.name
                )

        return weighted_sum / self.total
