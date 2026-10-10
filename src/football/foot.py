from __future__ import annotations

from enum import Enum
from random import choices, random

from .position import Position

MIN_WEAK_FOOT = 1
MAX_WEAK_FOOT = 5


class Foot(Enum):
    LEFT = "Left"
    RIGHT = "Right"

    @classmethod
    def random_for(cls, position: Position) -> Foot:
        return cls.LEFT if random() < LEFT_FOOTED_CHANCE[position] else cls.RIGHT

    def random_position(self) -> Position:
        positions = list(Position)
        weights = [
            LEFT_FOOTED_CHANCE[p] if self is Foot.LEFT else 1 - LEFT_FOOTED_CHANCE[p]
            for p in positions
        ]
        return choices(positions, weights)[0]


LEFT_FOOTED_CHANCE: dict[Position, float] = {
    Position.GOALKEEPER: 0.10,
    Position.CENTRE_BACK: 0.30,
    Position.LEFT_BACK: 0.70,
    Position.RIGHT_BACK: 0.08,
    Position.DEFENSIVE_MIDFIELDER: 0.20,
    Position.CENTRAL_MIDFIELDER: 0.22,
    Position.ATTACKING_MIDFIELDER: 0.25,
    Position.LEFT_MIDFIELDER: 0.60,
    Position.RIGHT_MIDFIELDER: 0.12,
    Position.LEFT_WINGER: 0.55,
    Position.RIGHT_WINGER: 0.30,
    Position.STRIKER: 0.20,
}


missing = set(Position) - LEFT_FOOTED_CHANCE.keys()
if missing:
    raise ValueError(
        f"No footedness chance defined for: {sorted(p.name for p in missing)}"
    )

invalid = {p.name: c for p, c in LEFT_FOOTED_CHANCE.items() if not 0 < c < 1}
if invalid:
    raise ValueError(f"Footedness chance must be strictly between 0 and 1: {invalid}")
