import random
from dataclasses import fields
from math import floor

from .aging import AGING_CLASS_OF, AgingClass
from .attributes import Attributes, BaseAttributes
from .development import (
    GAP_HEADROOM_FRACTION,
    GAP_SHAPE,
    MAX_GAP,
    OVERALL_CEILING,
    OVERALL_FLOOR,
    PEAK_AGE,
    START_AGE,
    gap_for,
)
from .generation import (
    OFF_ROLE_FLOOR,
    OFF_ROLE_FRACTION,
    OUTFIELD_GK_FLOOR,
    OUTFIELD_GK_FRACTION,
)
from .position import Position, PositionGroup
from .ratings import PROFILES, overall_rating


def stochastic_round(value: float) -> int:
    whole = floor(value)
    return whole + int(random.random() < value - whole)


MATURITY_AGE: dict[AgingClass, float] = {
    AgingClass.FAST: 21.0,
    AgingClass.MEDIUM: 23.0,
    AgingClass.SLOW: 25.0,
    AgingClass.MENTAL: PEAK_AGE,
}

if MATURITY_AGE.keys() != set(AgingClass):
    raise ValueError("Every aging class needs a maturity age")

MATURITY_PROGRESS: dict[AgingClass, float] = {
    aging_class: (age - START_AGE) / (PEAK_AGE - START_AGE)
    for aging_class, age in MATURITY_AGE.items()
}


def growth_progress(age: float, potential: int, offset: float) -> float:
    start_gap = min(MAX_GAP, GAP_HEADROOM_FRACTION * (potential - OVERALL_FLOOR))
    if start_gap <= 0:
        return 1.0

    ratio = gap_for(age, potential, offset) / start_gap
    return min(1.0, max(0.0, 1 - ratio ** (1 / GAP_SHAPE)))


def _weight_by_class(position: Position) -> dict[AgingClass, int]:
    weights = PROFILES[position]
    totals = {aging_class: 0 for aging_class in AgingClass}

    for group in fields(weights):
        group_weights = getattr(weights, group.name)
        for attribute in fields(group_weights):
            name = f"{group.name}.{attribute.name}"
            totals[AGING_CLASS_OF[name]] += getattr(group_weights, attribute.name)

    return totals


WEIGHT_BY_CLASS: dict[Position, dict[AgingClass, int]] = {
    position: _weight_by_class(position) for position in Position
}


def class_lag(aging_class: AgingClass, progress: float) -> float:
    maturity = MATURITY_PROGRESS[aging_class]
    return max(0.0, (maturity - progress) / maturity) ** GAP_SHAPE


def class_deficits(
    position: Position, age: float, potential: int, offset: float
) -> dict[AgingClass, float]:
    gap = gap_for(age, potential, offset)
    progress = growth_progress(age, potential, offset)
    lags = {aging_class: class_lag(aging_class, progress) for aging_class in AgingClass}

    weights = WEIGHT_BY_CLASS[position]
    mean_lag = sum(weights[c] * lags[c] for c in AgingClass) / sum(weights.values())
    if mean_lag <= 1e-12:
        return {aging_class: 0.0 for aging_class in AgingClass}

    return {
        aging_class: gap * lags[aging_class] / mean_lag for aging_class in AgingClass
    }


def class_increments(
    position: Position, age: float, potential: int, offset: float, delta: float
) -> dict[AgingClass, float]:
    if delta <= 0:
        return {aging_class: 0.0 for aging_class in AgingClass}

    now = class_deficits(position, age, potential, offset)
    later = class_deficits(position, age + 1, potential, offset)
    shares = {c: max(0.0, now[c] - later[c]) for c in AgingClass}

    weights = WEIGHT_BY_CLASS[position]
    weighted_share = sum(weights[c] * shares[c] for c in AgingClass) / sum(
        weights.values()
    )
    if weighted_share <= 1e-12:
        return {aging_class: delta for aging_class in AgingClass}

    scale = delta / weighted_share
    return {c: shares[c] * scale for c in AgingClass}


def class_levels(
    position: Position, age: float, potential: int, offset: float
) -> dict[AgingClass, float]:
    deficits = class_deficits(position, age, potential, offset)
    return {
        c: (potential - deficits[c]) * (1 - c.loss_fraction(age)) for c in AgingClass
    }


def expected_overall(
    position: Position, age: float, potential: int, offset: float
) -> int:
    levels = class_levels(position, age, potential, offset)
    weights = WEIGHT_BY_CLASS[position]
    return round(
        sum(weights[c] * levels[c] for c in AgingClass) / sum(weights.values())
    )


def potential_from_current(
    position: Position, age: float, overall: int, offset: float
) -> int:
    low, high = overall, OVERALL_CEILING
    while low < high:
        middle = (low + high) // 2
        if expected_overall(position, age, middle, offset) >= overall:
            high = middle
        else:
            low = middle + 1
    return low


GROWTH_WOBBLE = 0.5
DECLINE_WOBBLE = 0.5


def wobble(spread: float) -> float:
    return random.lognormvariate(-(spread**2) / 2, spread)


def growth_delta(
    position: Position,
    attributes: Attributes,
    age: float,
    potential: int,
    offset: float,
) -> float:
    if age - offset >= PEAK_AGE:
        return 0.0

    overall = overall_rating(attributes, position)
    target = potential - gap_for(age + 1, potential, offset)
    delta = max(0.0, target - overall) * wobble(GROWTH_WOBBLE)
    return min(delta, max(0.0, potential - overall))


def _off_role_baseline(group: str, is_goalkeeper: bool, overall: float) -> float:
    if group == "goalkeeping" and not is_goalkeeper:
        return max(OUTFIELD_GK_FRACTION * overall, OUTFIELD_GK_FLOOR)
    return max(OFF_ROLE_FRACTION * overall, OFF_ROLE_FLOOR)


def _spread_with_caps(
    weights: dict[str, int],
    shares: dict[str, float],
    room: dict[str, float],
    budget: float,
) -> dict[str, float]:
    gains = {name: 0.0 for name in weights}
    free = set(weights)

    while free and budget > 1e-9:
        denominator = sum(weights[n] * shares[n] for n in free)
        if denominator <= 1e-12:
            break

        scale = budget / denominator
        capped = {n for n in free if shares[n] * scale > room[n]}
        if not capped:
            for n in free:
                gains[n] = shares[n] * scale
            break

        for n in capped:
            gains[n] = room[n]
            budget -= weights[n] * room[n]
        free -= capped

    return gains


def grow_attributes(
    position: Position,
    attributes: Attributes,
    age: int,
    potential: int,
    offset: float,
) -> Attributes:
    delta = growth_delta(position, attributes, age, potential, offset)
    if delta <= 0:
        return attributes

    by_class = class_increments(position, age, potential, offset, delta)
    weights = PROFILES[position]
    is_goalkeeper = position.group is PositionGroup.GOALKEEPER

    old_overall = overall_rating(attributes, position)
    new_overall = old_overall + delta

    current: dict[str, int] = {}
    on_role: dict[str, int] = {}
    off_role_gain: dict[str, float] = {}

    for group in fields(Attributes):
        group_weights = getattr(weights, group.name)
        group_values = getattr(attributes, group.name)

        for attribute in fields(group_weights):
            name = f"{group.name}.{attribute.name}"
            weight = getattr(group_weights, attribute.name)
            current[name] = getattr(group_values, attribute.name)

            if weight > 0:
                on_role[name] = weight
            else:
                baseline_change = _off_role_baseline(
                    group.name, is_goalkeeper, new_overall
                ) - _off_role_baseline(group.name, is_goalkeeper, old_overall)
                off_role_gain[name] = (
                    by_class[AGING_CLASS_OF[name]] * baseline_change / delta
                )

    on_role_gain = _spread_with_caps(
        on_role,
        {name: by_class[AGING_CLASS_OF[name]] for name in on_role},
        {name: BaseAttributes.MAX - current[name] for name in on_role},
        delta * weights.total,
    )

    values: dict[str, dict[str, int]] = {}
    for name, value in current.items():
        group_name, attribute_name = name.split(".")
        gain = on_role_gain[name] if name in on_role else off_role_gain[name]
        values.setdefault(group_name, {})[attribute_name] = min(
            BaseAttributes.MAX, stochastic_round(value + gain)
        )

    return Attributes(**{g.name: g.type(**values[g.name]) for g in fields(Attributes)})


def _floor(group: str, weight: int, is_goalkeeper: bool) -> int:
    if weight > 0:
        return BaseAttributes.MIN
    if group == "goalkeeping" and not is_goalkeeper:
        return OUTFIELD_GK_FLOOR
    return OFF_ROLE_FLOOR


def decline_attributes(
    position: Position, attributes: Attributes, age: int
) -> Attributes:
    ratios: dict[AgingClass, float] = {}
    for aging_class in AgingClass:
        before = 1 - aging_class.loss_fraction(age)
        after = 1 - aging_class.loss_fraction(age + 1)
        ratios[aging_class] = after / before if before > 0 else 0.0

    if all(ratio == 1.0 for ratio in ratios.values()):
        return attributes

    shock = wobble(DECLINE_WOBBLE)
    ratios = {c: max(0.0, 1 - shock * (1 - r)) for c, r in ratios.items()}

    weights = PROFILES[position]
    is_goalkeeper = position.group is PositionGroup.GOALKEEPER
    values: dict[str, dict[str, int]] = {}

    for group in fields(Attributes):
        group_weights = getattr(weights, group.name)
        group_values = getattr(attributes, group.name)

        for attribute in fields(group_weights):
            name = f"{group.name}.{attribute.name}"
            current = getattr(group_values, attribute.name)
            floor = _floor(
                group.name, getattr(group_weights, attribute.name), is_goalkeeper
            )
            declined = stochastic_round(current * ratios[AGING_CLASS_OF[name]])
            values.setdefault(group.name, {})[attribute.name] = max(
                min(floor, current), declined
            )

    return Attributes(**{g.name: g.type(**values[g.name]) for g in fields(Attributes)})
