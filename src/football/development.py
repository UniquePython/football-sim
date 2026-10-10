import random

from .attributes import BaseAttributes
from .generation import TIERS

START_AGE = 16
PEAK_AGE = 26.5
MAX_GAP = 20.0
GAP_SHAPE = 1.5

OFFSET_SIGMA = 1.5
OFFSET_LIMIT = 3.0

GAP_HEADROOM_FRACTION = 0.75

OVERALL_FLOOR = min(tier.low for tier in TIERS)
OVERALL_CEILING = BaseAttributes.MAX


def generate_development_offset() -> float:
    return max(-OFFSET_LIMIT, min(OFFSET_LIMIT, random.gauss(0, OFFSET_SIGMA)))


def curve_gap(age: float) -> float:
    progress = max(0.0, (PEAK_AGE - age) / (PEAK_AGE - START_AGE))
    return MAX_GAP * progress**GAP_SHAPE


def gap_for(age: float, potential: int, offset: float) -> float:
    headroom_cap = GAP_HEADROOM_FRACTION * (potential - OVERALL_FLOOR)
    return min(curve_gap(age - offset), headroom_cap)


def overall_from_potential(age: float, potential: int, offset: float) -> int:
    return round(potential - gap_for(age, potential, offset))


def potential_from_overall(age: float, overall: int, offset: float) -> int:
    headroom_cap = (
        GAP_HEADROOM_FRACTION
        * max(0, overall - OVERALL_FLOOR)
        / (1 - GAP_HEADROOM_FRACTION)
    )
    gap = min(curve_gap(age - offset), headroom_cap)
    return min(OVERALL_CEILING, round(overall + gap))
