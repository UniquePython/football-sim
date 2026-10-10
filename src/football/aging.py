from dataclasses import fields
from enum import Enum
from typing import get_type_hints

from .attributes import Attributes

DECLINE_SHAPE = 1.5
REFERENCE_RATING = 75


class AgingClass(Enum):
    FAST = (27, 0.80)
    MEDIUM = (29, 0.55)
    SLOW = (31, 0.30)
    MENTAL = (33, 0.20)

    def __init__(self, start_age: int, rate: float) -> None:
        self.start_age = start_age
        self.rate = rate

    def loss_fraction(self, age: float) -> float:
        points = self.rate * max(0.0, age - self.start_age) ** DECLINE_SHAPE
        return min(1.0, points / REFERENCE_RATING)


ATTRIBUTES_BY_CLASS: dict[AgingClass, tuple[str, ...]] = {
    AgingClass.FAST: (
        "pace.acceleration",
        "pace.sprint_speed",
        "dribbling.agility",
    ),
    AgingClass.MEDIUM: (
        "physical.stamina",
        "physical.jumping",
        "shooting.shot_power",
        "defending.slide_tackling",
    ),
    AgingClass.SLOW: (
        "physical.strength",
        "dribbling.balance",
        "dribbling.ball_control",
        "dribbling.dribbling",
        "shooting.finishing",
        "shooting.long_shots",
        "passing.short_passing",
        "passing.long_passing",
        "passing.curve",
        "passing.crossing",
        "defending.standing_tackling",
        "defending.heading",
        "goalkeeping.handling",
        "goalkeeping.diving",
        "goalkeeping.reflexes",
    ),
    AgingClass.MENTAL: (
        "passing.vision",
        "shooting.positioning",
        "defending.positioning",
        "goalkeeping.positioning",
        "defending.interceptions",
    ),
}

AGING_CLASS_OF: dict[str, AgingClass] = {
    attribute: aging_class
    for aging_class, attributes in ATTRIBUTES_BY_CLASS.items()
    for attribute in attributes
}


def _all_attribute_names() -> set[str]:
    group_types = get_type_hints(Attributes)
    return {
        f"{group.name}.{attribute.name}"
        for group in fields(Attributes)
        for attribute in fields(group_types[group.name])
    }


_expected = _all_attribute_names()
_missing = _expected - AGING_CLASS_OF.keys()
_unknown = AGING_CLASS_OF.keys() - _expected
if _missing or _unknown:
    raise ValueError(
        f"Aging classes out of sync with Attributes: "
        f"missing {sorted(_missing)}, unknown {sorted(_unknown)}"
    )
if sum(len(attrs) for attrs in ATTRIBUTES_BY_CLASS.values()) != len(AGING_CLASS_OF):
    raise ValueError("An attribute is assigned to more than one aging class")


def loss_fraction(attribute: str, age: float) -> float:
    return AGING_CLASS_OF[attribute].loss_fraction(age)
