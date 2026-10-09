from __future__ import annotations

from enum import Enum
from random import choice


class PositionGroup(Enum):
    ATTACKER = "Attacker"
    MIDFIELDER = "Midfielder"
    DEFENDER = "Defender"
    GOALKEEPER = "Goalkeeper"


class Position(Enum):
    # Attackers
    LEFT_WINGER = ("LW", PositionGroup.ATTACKER)
    RIGHT_WINGER = ("RW", PositionGroup.ATTACKER)
    STRIKER = ("ST", PositionGroup.ATTACKER)

    # Midfielders
    DEFENSIVE_MIDFIELDER = ("DM", PositionGroup.MIDFIELDER)
    CENTRAL_MIDFIELDER = ("CM", PositionGroup.MIDFIELDER)
    ATTACKING_MIDFIELDER = ("AM", PositionGroup.MIDFIELDER)
    LEFT_MIDFIELDER = ("LM", PositionGroup.MIDFIELDER)
    RIGHT_MIDFIELDER = ("RM", PositionGroup.MIDFIELDER)

    # Defenders
    CENTRE_BACK = ("CB", PositionGroup.DEFENDER)
    LEFT_BACK = ("LB", PositionGroup.DEFENDER)
    RIGHT_BACK = ("RB", PositionGroup.DEFENDER)

    # Goalkeeper has no further subdivision here
    GOALKEEPER = ("GK", PositionGroup.GOALKEEPER)

    def __init__(self, abbreviation: str, group: PositionGroup):
        self.abbreviation = abbreviation
        self.group = group

    @classmethod
    def random(cls) -> Position:
        return choice(list(cls))
