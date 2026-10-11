from __future__ import annotations

from dataclasses import fields
from math import isclose, sqrt
from typing import TYPE_CHECKING

from .attributes import BaseAttributes
from .position import Position
from .ratings import PROFILES, overall_rating
from .weights import Weights

if TYPE_CHECKING:
    from .player import Player

# Rating points lost per unit of profile distance. A distance of 0 means the
# slot's profile is identical to the player's natural one, 1 means no overlap.
OUT_OF_POSITION_PENALTY = 19.0


def _profile_vector(weights: Weights) -> tuple[int, ...]:
    return tuple(
        getattr(getattr(weights, group.name), attribute.name)
        for group in fields(Weights)
        for attribute in fields(getattr(weights, group.name))
    )


def _cosine_distance(a: tuple[int, ...], b: tuple[int, ...]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    similarity = dot / (sqrt(sum(x * x for x in a)) * sqrt(sum(y * y for y in b)))
    return max(0.0, 1.0 - similarity)


_VECTORS = {position: _profile_vector(PROFILES[position]) for position in Position}

POSITION_DISTANCE: dict[tuple[Position, Position], float] = {
    (natural, slot): _cosine_distance(_VECTORS[natural], _VECTORS[slot])
    for natural in Position
    for slot in Position
}

_bad_diagonal = {
    p.name: POSITION_DISTANCE[p, p]
    for p in Position
    if not isclose(POSITION_DISTANCE[p, p], 0.0, abs_tol=1e-9)
}
if _bad_diagonal:
    raise ValueError(f"A position must be at distance 0 from itself: {_bad_diagonal}")

_asymmetric = sorted(
    f"{a.name}/{b.name}"
    for a in Position
    for b in Position
    if not isclose(POSITION_DISTANCE[a, b], POSITION_DISTANCE[b, a], abs_tol=1e-9)
)
if _asymmetric:
    raise ValueError(f"Position distances must be symmetric: {_asymmetric}")

_out_of_range = sorted(
    f"{a.name}/{b.name}"
    for (a, b), distance in POSITION_DISTANCE.items()
    if not 0.0 <= distance <= 1.0
)
if _out_of_range:
    raise ValueError(f"Position distances must be between 0 and 1: {_out_of_range}")


def slot_rating(player: Player, slot: Position) -> float:
    distance = POSITION_DISTANCE[player.position, slot]
    rating = (
        overall_rating(player.attributes, slot) - OUT_OF_POSITION_PENALTY * distance
    )
    return max(float(BaseAttributes.MIN), rating)
