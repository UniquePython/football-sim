import random
from dataclasses import dataclass, fields
from enum import StrEnum

from .utils import require_condition, require_type_and_not_none


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

TIERS = (
    QualityTier(QualityTierName.BAD, 40, 49, 35.0),
    QualityTier(QualityTierName.AVERAGE, 50, 59, 40.0),
    QualityTier(QualityTierName.GOOD, 60, 69, 18.0),
    QualityTier(QualityTierName.VGOOD, 70, 79, 5.0),
    QualityTier(QualityTierName.VVGOOD, 80, 89, 1.8),
    QualityTier(QualityTierName.ELITE, 90, 99, 0.2),
)

WEIGHTS = weights = [tier.weight for tier in TIERS]


def generate_base_quality() -> int:
    tier = random.choices(TIERS, WEIGHTS)[0]
    mode = tier.low + TIER_PEAK_FRACTION * (tier.high - tier.low)
    return round(random.triangular(tier.low - 0.5, tier.high + 0.5, mode))
