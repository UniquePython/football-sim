from .attributes import Attributes
from .position import Position
from .weights import (
    DefendingWeights,
    DribblingWeights,
    GoalKeepingWeights,
    PaceWeights,
    PassingWeights,
    PhysicalWeights,
    ShootingWeights,
    Weights,
)

GOALKEEPER = Weights(
    goalkeeping=GoalKeepingWeights(reflexes=10, positioning=10, diving=9, handling=9),
    passing=PassingWeights(short_passing=3, long_passing=3, vision=2),
    physical=PhysicalWeights(jumping=2, strength=1),
    dribbling=DribblingWeights(agility=2, balance=1, ball_control=1),
)

CENTRE_BACK = Weights(
    defending=DefendingWeights(
        positioning=10,
        standing_tackling=9,
        heading=9,
        interceptions=8,
        slide_tackling=3,
    ),
    physical=PhysicalWeights(strength=4, jumping=4, stamina=2),
    pace=PaceWeights(sprint_speed=4, acceleration=3),
    passing=PassingWeights(short_passing=3, long_passing=2, vision=1),
    dribbling=DribblingWeights(ball_control=1, balance=1),
)

FULL_BACK = Weights(
    defending=DefendingWeights(
        standing_tackling=8, positioning=7, interceptions=6, slide_tackling=4, heading=3
    ),
    physical=PhysicalWeights(stamina=9, strength=3, jumping=2),
    pace=PaceWeights(sprint_speed=8, acceleration=6),
    passing=PassingWeights(
        crossing=6, short_passing=5, long_passing=2, vision=2, curve=1
    ),
    dribbling=DribblingWeights(ball_control=3, agility=3, dribbling=2, balance=1),
)

DEFENSIVE_MIDFIELDER = Weights(
    defending=DefendingWeights(
        interceptions=9, standing_tackling=9, positioning=8, slide_tackling=3, heading=3
    ),
    passing=PassingWeights(short_passing=8, long_passing=5, vision=5),
    physical=PhysicalWeights(stamina=7, strength=6, jumping=2),
    dribbling=DribblingWeights(ball_control=4, balance=2, agility=1, dribbling=1),
    pace=PaceWeights(acceleration=2, sprint_speed=2),
)

CENTRAL_MIDFIELDER = Weights(
    passing=PassingWeights(short_passing=9, vision=8, long_passing=6),
    dribbling=DribblingWeights(ball_control=8, dribbling=4, agility=3, balance=3),
    physical=PhysicalWeights(stamina=8, strength=4, jumping=1),
    defending=DefendingWeights(
        standing_tackling=5, interceptions=5, positioning=4, slide_tackling=2, heading=1
    ),
    shooting=ShootingWeights(long_shots=3, positioning=2, finishing=2, shot_power=2),
    pace=PaceWeights(acceleration=2, sprint_speed=2),
)

ATTACKING_MIDFIELDER = Weights(
    passing=PassingWeights(
        vision=9, short_passing=8, long_passing=3, curve=3, crossing=2
    ),
    dribbling=DribblingWeights(ball_control=9, dribbling=8, agility=6, balance=3),
    shooting=ShootingWeights(finishing=5, positioning=5, long_shots=5, shot_power=3),
    pace=PaceWeights(acceleration=4, sprint_speed=2),
    physical=PhysicalWeights(stamina=3, strength=1),
)

WIDE_MIDFIELDER = Weights(
    passing=PassingWeights(
        crossing=9, short_passing=6, vision=4, long_passing=3, curve=2
    ),
    physical=PhysicalWeights(stamina=9, strength=2),
    pace=PaceWeights(sprint_speed=8, acceleration=7),
    dribbling=DribblingWeights(dribbling=6, ball_control=6, agility=4, balance=2),
    defending=DefendingWeights(
        positioning=3, interceptions=3, standing_tackling=3, slide_tackling=1
    ),
    shooting=ShootingWeights(finishing=2, positioning=2, long_shots=2, shot_power=1),
)

WINGER = Weights(
    dribbling=DribblingWeights(dribbling=9, ball_control=8, agility=7, balance=3),
    pace=PaceWeights(acceleration=9, sprint_speed=9),
    passing=PassingWeights(crossing=6, short_passing=4, vision=3, curve=3),
    shooting=ShootingWeights(finishing=5, positioning=4, shot_power=3, long_shots=3),
    physical=PhysicalWeights(stamina=3, strength=1),
)

STRIKER = Weights(
    shooting=ShootingWeights(finishing=10, positioning=9, shot_power=6, long_shots=3),
    dribbling=DribblingWeights(ball_control=6, dribbling=4, agility=3, balance=3),
    pace=PaceWeights(acceleration=6, sprint_speed=6),
    physical=PhysicalWeights(strength=5, jumping=5, stamina=3),
    defending=DefendingWeights(heading=5),
    passing=PassingWeights(short_passing=3, vision=2, curve=1),
)

PROFILES: dict[Position, Weights] = {
    Position.GOALKEEPER: GOALKEEPER,
    Position.CENTRE_BACK: CENTRE_BACK,
    Position.LEFT_BACK: FULL_BACK,
    Position.RIGHT_BACK: FULL_BACK,
    Position.DEFENSIVE_MIDFIELDER: DEFENSIVE_MIDFIELDER,
    Position.CENTRAL_MIDFIELDER: CENTRAL_MIDFIELDER,
    Position.ATTACKING_MIDFIELDER: ATTACKING_MIDFIELDER,
    Position.LEFT_MIDFIELDER: WIDE_MIDFIELDER,
    Position.RIGHT_MIDFIELDER: WIDE_MIDFIELDER,
    Position.LEFT_WINGER: WINGER,
    Position.RIGHT_WINGER: WINGER,
    Position.STRIKER: STRIKER,
}


missing = set(Position) - PROFILES.keys()
if missing:
    raise ValueError(f"No weights defined for: {sorted(p.name for p in missing)}")


def overall_rating(attributes: Attributes, position: Position) -> float:
    return PROFILES[position].overall(attributes)
