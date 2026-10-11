from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .assignment import min_cost_assignment
from .fit import slot_rating
from .formation import SLOT_COUNT, Formation
from .position import Position, PositionGroup

if TYPE_CHECKING:
    from .player import Player


@dataclass(frozen=True, slots=True)
class Lineup:
    """Eleven players placed into a formation.

    starters[i] plays formation.slots[i], and ratings[i] is how good he is there.
    reserves are the remaining players, best overall first.

    Every strength is a mean of slot ratings. A slot belongs to a line through
    its position's group, so overall strength is the average of the four line
    strengths, each weighted by how many slots that line has.
    """

    formation: Formation
    starters: tuple[Player, ...]
    ratings: tuple[float, ...]
    reserves: tuple[Player, ...]

    @property
    def strength(self) -> float:
        return sum(self.ratings) / len(self.ratings)

    @property
    def assignments(self) -> tuple[tuple[Position, Player, float], ...]:
        return tuple(zip(self.formation.slots, self.starters, self.ratings))

    def line_strength(self, group: PositionGroup) -> float:
        ratings = [
            rating
            for slot, rating in zip(self.formation.slots, self.ratings)
            if slot.group is group
        ]
        if not ratings:
            raise ValueError(
                f"Formation {self.formation.label} has no {group.value.lower()} slots"
            )
        return sum(ratings) / len(ratings)

    @property
    def defence_strength(self) -> float:
        return self.line_strength(PositionGroup.DEFENDER)

    @property
    def midfield_strength(self) -> float:
        return self.line_strength(PositionGroup.MIDFIELDER)

    @property
    def attack_strength(self) -> float:
        return self.line_strength(PositionGroup.ATTACKER)

    @property
    def goalkeeper_strength(self) -> float:
        return self.line_strength(PositionGroup.GOALKEEPER)


def best_lineup(formation: Formation, players: Sequence[Player]) -> Lineup:
    if len(players) < SLOT_COUNT:
        raise ValueError(
            f"Need at least {SLOT_COUNT} players for a lineup, got {len(players)}"
        )
    if len({id(player) for player in players}) != len(players):
        raise ValueError("The same player cannot appear twice in a squad")

    table = [
        [slot_rating(player, slot) for player in players] for slot in formation.slots
    ]
    chosen = min_cost_assignment([[-rating for rating in row] for row in table])

    taken = set(chosen)
    reserves = sorted(
        (player for index, player in enumerate(players) if index not in taken),
        key=lambda player: player.overall,
        reverse=True,
    )

    return Lineup(
        formation=formation,
        starters=tuple(players[column] for column in chosen),
        ratings=tuple(table[row][column] for row, column in enumerate(chosen)),
        reserves=tuple(reserves),
    )
