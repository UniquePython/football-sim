from dataclasses import dataclass, fields
from typing import ClassVar

from .utils import require_condition, require_type_and_not_none


class BaseAttributes:
    MIN: ClassVar[int] = 1
    MAX: ClassVar[int] = 99

    def __post_init__(self) -> None:
        for field in fields(self):
            name = field.name
            value = getattr(self, name)

            require_condition(
                require_type_and_not_none(
                    value,
                    int,
                    f"Attribute {name} must be of type int",
                    f"Attribute {name} must not be None",
                ),
                lambda value: self.MIN <= value <= self.MAX,
                f"Attribute {name} must be between {self.MIN} and {self.MAX}",
            )


@dataclass(slots=True)
class DribblingAttributes(BaseAttributes):
    agility: int
    balance: int
    ball_control: int
    dribbling: int


@dataclass(slots=True)
class ShootingAttributes(BaseAttributes):
    positioning: int
    finishing: int
    shot_power: int
    long_shots: int


@dataclass(slots=True)
class PassingAttributes(BaseAttributes):
    vision: int
    crossing: int
    short_passing: int
    long_passing: int
    curve: int


@dataclass(slots=True)
class DefendingAttributes(BaseAttributes):
    positioning: int
    interceptions: int
    heading: int
    standing_tackling: int
    slide_tackling: int


@dataclass(slots=True)
class PaceAttributes(BaseAttributes):
    acceleration: int
    sprint_speed: int


@dataclass(slots=True)
class PhysicalAttributes(BaseAttributes):
    jumping: int
    strength: int
    stamina: int


@dataclass(slots=True)
class GoalKeepingAttributes(BaseAttributes):
    positioning: int
    diving: int
    handling: int
    reflexes: int


@dataclass(slots=True)
class Attributes:
    dribbling: DribblingAttributes
    shooting: ShootingAttributes
    passing: PassingAttributes
    defending: DefendingAttributes
    pace: PaceAttributes
    physical: PhysicalAttributes
    goalkeeping: GoalKeepingAttributes

    def __post_init__(self) -> None:
        expected_types = {
            "dribbling": DribblingAttributes,
            "shooting": ShootingAttributes,
            "passing": PassingAttributes,
            "defending": DefendingAttributes,
            "pace": PaceAttributes,
            "physical": PhysicalAttributes,
            "goalkeeping": GoalKeepingAttributes,
        }

        for field in fields(self):
            name = field.name
            expected_type = expected_types[name]

            require_type_and_not_none(
                getattr(self, name),
                expected_type,
                f"Attribute {name} must be of type {expected_type.__name__}",
                f"Attribute {name} must not be None",
            )
