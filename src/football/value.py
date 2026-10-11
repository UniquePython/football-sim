import math
from bisect import bisect_right

# (rating, value) anchors: the typical price of a prime-age player whose
# overall equals his potential
VALUE_ANCHORS: tuple[tuple[int, float], ...] = (
    (40, 16_000),
    (50, 78_000),
    (60, 350_000),
    (70, 1_700_000),
    (80, 8_600_000),
    (90, 45_600_000),
    (99, 250_000_000),
)

# (age, multiplier) anchors: the share of value kept once past his prime
AGE_DECLINE_ANCHORS: tuple[tuple[int, float], ...] = (
    (28, 1.00),
    (29, 0.96),
    (30, 0.90),
    (31, 0.80),
    (32, 0.68),
    (33, 0.55),
    (34, 0.44),
    (35, 0.33),
    (36, 0.23),
    (38, 0.10),
    (45, 0.03),
)

GROWTH_WEIGHT = 0.4

_RATINGS = [rating for rating, _ in VALUE_ANCHORS]
_LOG_VALUES = [math.log(value) for _, value in VALUE_ANCHORS]
_DECLINE_AGES = [age for age, _ in AGE_DECLINE_ANCHORS]
_DECLINE_MULTIPLIERS = [multiplier for _, multiplier in AGE_DECLINE_ANCHORS]


def _interpolate(xs: list[int], ys: list[float], x: float) -> float:
    x = min(max(x, xs[0]), xs[-1])

    upper = min(bisect_right(xs, x), len(xs) - 1)
    lower = upper - 1

    fraction = (x - xs[lower]) / (xs[upper] - xs[lower])
    return ys[lower] + fraction * (ys[upper] - ys[lower])


def base_value(rating: float) -> float:
    return math.exp(_interpolate(_RATINGS, _LOG_VALUES, rating))


def effective_rating(overall: int, growth_headroom: int) -> float:
    return overall + GROWTH_WEIGHT * growth_headroom


def age_decline(age: float) -> float:
    return _interpolate(_DECLINE_AGES, _DECLINE_MULTIPLIERS, age)


def market_value(overall: int, growth_headroom: int, age: float) -> float:
    return base_value(effective_rating(overall, growth_headroom)) * age_decline(age)


VALUE_SIGNIFICANT_DIGITS = 2


def round_value(value: float) -> int:
    return int(float(f"{value:.{VALUE_SIGNIFICANT_DIGITS}g}"))
