from __future__ import annotations

from collections import Counter
from enum import Enum

from .position import Position

GK = Position.GOALKEEPER
LB = Position.LEFT_BACK
CB = Position.CENTRE_BACK
RB = Position.RIGHT_BACK
DM = Position.DEFENSIVE_MIDFIELDER
CM = Position.CENTRAL_MIDFIELDER
AM = Position.ATTACKING_MIDFIELDER
LM = Position.LEFT_MIDFIELDER
RM = Position.RIGHT_MIDFIELDER
LW = Position.LEFT_WINGER
RW = Position.RIGHT_WINGER
ST = Position.STRIKER

SLOT_COUNT = 11


class Formation(Enum):
    # Slots run GK first, then back to front, left to right.
    # The order is only for readability: never rely on it for logic.

    # Back four
    FOUR_THREE_THREE = ("4-3-3", (GK, LB, CB, CB, RB, DM, CM, CM, LW, ST, RW))
    FOUR_TWO_THREE_ONE = ("4-2-3-1", (GK, LB, CB, CB, RB, DM, DM, LW, AM, RW, ST))
    FOUR_ONE_TWO_ONE_TWO = ("4-1-2-1-2", (GK, LB, CB, CB, RB, DM, CM, CM, AM, ST, ST))
    FOUR_FOUR_TWO = ("4-4-2", (GK, LB, CB, CB, RB, LM, CM, CM, RM, ST, ST))
    FOUR_TWO_TWO_TWO = ("4-2-2-2", (GK, LB, CB, CB, RB, DM, DM, AM, AM, ST, ST))
    FOUR_ONE_FOUR_ONE = ("4-1-4-1", (GK, LB, CB, CB, RB, DM, LM, CM, CM, RM, ST))
    FOUR_THREE_TWO_ONE = ("4-3-2-1", (GK, LB, CB, CB, RB, DM, CM, CM, AM, AM, ST))
    FOUR_TWO_FOUR = ("4-2-4", (GK, LB, CB, CB, RB, DM, CM, LW, ST, ST, RW))

    # Back three
    THREE_FOUR_THREE = ("3-4-3", (GK, CB, CB, CB, LM, CM, CM, RM, LW, ST, RW))
    THREE_FOUR_ONE_TWO = ("3-4-1-2", (GK, CB, CB, CB, LM, CM, CM, RM, AM, ST, ST))
    THREE_FIVE_TWO = ("3-5-2", (GK, CB, CB, CB, LM, CM, DM, CM, RM, ST, ST))
    THREE_FOUR_TWO_ONE = ("3-4-2-1", (GK, CB, CB, CB, LM, CM, CM, RM, AM, AM, ST))

    # Back five
    FIVE_THREE_TWO = ("5-3-2", (GK, LB, CB, CB, CB, RB, DM, CM, CM, ST, ST))
    FIVE_TWO_THREE = ("5-2-3", (GK, LB, CB, CB, CB, RB, DM, CM, LW, ST, RW))

    def __init__(self, label: str, slots: tuple[Position, ...]) -> None:
        self.label = label
        self.slots = slots


def _shape(slots: tuple[Position, ...]) -> frozenset[tuple[Position, int]]:
    return frozenset(Counter(slots).items())


_wrong_size = {f.label: len(f.slots) for f in Formation if len(f.slots) != SLOT_COUNT}
if _wrong_size:
    raise ValueError(f"Formations must have exactly {SLOT_COUNT} slots: {_wrong_size}")

_bad_keepers = {f.label: f.slots.count(GK) for f in Formation if f.slots.count(GK) != 1}
if _bad_keepers:
    raise ValueError(f"Formations must have exactly one goalkeeper: {_bad_keepers}")

_seen: dict[frozenset[tuple[Position, int]], str] = {}
for _formation in Formation:
    _key = _shape(_formation.slots)
    if _key in _seen:
        raise ValueError(
            f"Formations {_seen[_key]!r} and {_formation.label!r} have identical slots"
        )
    _seen[_key] = _formation.label
