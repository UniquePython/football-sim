import random
from dataclasses import dataclass, fields
from enum import StrEnum
from math import sqrt

from .aging import AGING_CLASS_OF, AgingClass
from .attributes import Attributes, BaseAttributes, GoalKeepingAttributes
from .foot import MAX_WEAK_FOOT, MIN_WEAK_FOOT
from .position import Position, PositionGroup
from .ratings import PROFILES
from .utils import require_condition, require_type, require_type_and_not_none


class QualityTierName(StrEnum):
    ELITE = "Elite"
    VVGOOD = "Very Very Good"
    VGOOD = "Very Good"
    GOOD = "Good"
    AVERAGE = "Average"
    BAD = "Bad"


@dataclass(frozen=True, slots=True)
class QualityTier:
    name: QualityTierName
    low: int
    high: int
    weight: float

    def __post_init__(self) -> None:
        expected_types = {
            "name": QualityTierName,
            "low": int,
            "high": int,
            "weight": float,
        }

        for field in fields(self):
            name = field.name
            expected_type = expected_types[name]
            value = getattr(self, name)

            require_type_and_not_none(
                value,
                expected_type,
                f"QualityTier field {name} must be of type {expected_type.__name__}",
                f"QualityTier field {name} must not be None",
            )

            if name != "name":
                require_condition(
                    value,
                    lambda value: value > 0,
                    f"QualityTier field {name} must be greater than 0",
                )

        if self.low > self.high:
            raise ValueError("Low cannot be higher than high")


TIER_PEAK_FRACTION = 0.4

SPREAD_SIGMA = 5.0
GROUP_CORRELATION = 0.7

OFF_ROLE_FRACTION = 0.5
OFF_ROLE_FLOOR = 20
OFF_ROLE_NOISE_SCALE = 0.5

OUTFIELD_GK_FRACTION = 0.2
OUTFIELD_GK_FLOOR = 10
OUTFIELD_GK_NOISE_SCALE = 0.2

WEAK_FOOT_MEAN_AT_MIN = 2.5
WEAK_FOOT_MEAN_AT_MAX = 3.5
WEAK_FOOT_SIGMA = 0.8

TIERS = (
    QualityTier(QualityTierName.BAD, 40, 49, 35.0),
    QualityTier(QualityTierName.AVERAGE, 50, 59, 40.0),
    QualityTier(QualityTierName.GOOD, 60, 69, 18.0),
    QualityTier(QualityTierName.VGOOD, 70, 79, 5.0),
    QualityTier(QualityTierName.VVGOOD, 80, 89, 1.8),
    QualityTier(QualityTierName.ELITE, 90, 99, 0.2),
)

WEIGHTS = [tier.weight for tier in TIERS]


def generate_potential() -> int:
    tier = random.choices(TIERS, WEIGHTS)[0]
    mode = tier.low + TIER_PEAK_FRACTION * (tier.high - tier.low)
    return round(random.triangular(tier.low - 0.5, tier.high + 0.5, mode))


def generate_weak_foot(overall: int) -> int:
    low = min(tier.low for tier in TIERS)
    high = BaseAttributes.MAX
    progress = min(1.0, max(0.0, (overall - low) / (high - low)))

    mean = WEAK_FOOT_MEAN_AT_MIN + progress * (
        WEAK_FOOT_MEAN_AT_MAX - WEAK_FOOT_MEAN_AT_MIN
    )

    return min(
        MAX_WEAK_FOOT, max(MIN_WEAK_FOOT, round(random.gauss(mean, WEAK_FOOT_SIGMA)))
    )


@dataclass(slots=True)
class _Slot:
    group: str
    name: str
    weight: int
    value: float
    floor: int


def generate_attributes(
    position: Position,
    target: int,
    levels: dict[AgingClass, float] | None = None,
) -> Attributes:
    require_type(target, int, "Target overall must be of type int")
    require_condition(
        target,
        lambda t: BaseAttributes.MIN <= t <= BaseAttributes.MAX,
        f"Target overall must be between {BaseAttributes.MIN} and {BaseAttributes.MAX}",
    )

    weights = PROFILES[position]
    is_goalkeeper = position.group is PositionGroup.GOALKEEPER

    shared_sigma = SPREAD_SIGMA * sqrt(GROUP_CORRELATION)
    individual_sigma = SPREAD_SIGMA * sqrt(1 - GROUP_CORRELATION)

    slots: list[_Slot] = []

    for group in fields(Attributes):
        group_weights = getattr(weights, group.name)
        shared = random.gauss(0, shared_sigma)

        for attribute in fields(group_weights):
            weight = getattr(group_weights, attribute.name)
            level = (
                target
                if levels is None
                else levels[AGING_CLASS_OF[f"{group.name}.{attribute.name}"]]
            )

            if weight > 0:
                baseline, scale, floor = level, 1.0, BaseAttributes.MIN
            elif group.type is GoalKeepingAttributes and not is_goalkeeper:
                baseline = max(OUTFIELD_GK_FRACTION * level, OUTFIELD_GK_FLOOR)
                scale, floor = OUTFIELD_GK_NOISE_SCALE, OUTFIELD_GK_FLOOR
            else:
                baseline = max(OFF_ROLE_FRACTION * level, OFF_ROLE_FLOOR)
                scale, floor = OFF_ROLE_NOISE_SCALE, OFF_ROLE_FLOOR

            value = baseline + scale * (shared + random.gauss(0, individual_sigma))
            slots.append(_Slot(group.name, attribute.name, weight, value, floor))

    _correct_on_role(slots, target)
    return _build(slots)


def _correct_on_role(slots: list[_Slot], target: int) -> None:
    on_role = [s for s in slots if s.weight > 0]
    total_weight = sum(s.weight for s in on_role)

    for _ in range(len(on_role) + 2):
        for s in on_role:
            s.value = max(BaseAttributes.MIN, min(BaseAttributes.MAX, s.value))

        error = target - sum(s.weight * s.value for s in on_role) / total_weight
        if abs(error) < 1e-6:
            return

        if error > 0:
            free = [s for s in on_role if s.value < BaseAttributes.MAX]
        else:
            free = [s for s in on_role if s.value > BaseAttributes.MIN]

        free_weight = sum(s.weight for s in free)
        if free_weight == 0:
            return

        shift = error * total_weight / free_weight
        for s in free:
            s.value += shift


def _build(slots: list[_Slot]) -> Attributes:
    values: dict[str, dict[str, int]] = {}

    for s in slots:
        rounded = max(s.floor, min(BaseAttributes.MAX, round(s.value)))
        values.setdefault(s.group, {})[s.name] = rounded

    return Attributes(**{g.name: g.type(**values[g.name]) for g in fields(Attributes)})
