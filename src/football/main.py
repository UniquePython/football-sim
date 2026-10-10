import argparse
from collections.abc import Callable
from statistics import mean

from .foot import Foot
from .generation import TIERS, generate_attributes, generate_potential
from .nationality import Nationality
from .player import Player
from .position import Position
from .ratings import overall_rating

# ========== DEMO ==========


def show_example_players() -> None:
    hand_made = Player(
        nationality=Nationality.UK,
        age=16,
        position=Position.ATTACKING_MIDFIELDER,
        overall=69,
        foot=Foot.LEFT,
        weak_foot=2,
        development_offset=0.0,
    )
    random_player = Player()

    print(hand_made)
    print(random_player)

    # print(repr(hand_made))
    # print(repr(random_player))


# ========== CHECKS ==========


def check_age_distribution(n: int = 10_000) -> None:
    import matplotlib.pyplot as plt

    ages = [Player().age for _ in range(n)]

    plt.hist(ages, bins=range(15, 44), edgecolor="black")
    plt.xlabel("Player age")
    plt.ylabel("Number of players")
    plt.title(f"Distribution of football player ages ({n:,} players)")
    plt.xticks(range(16, 43))
    plt.tight_layout()
    plt.show()


def check_base_quality_distribution(n: int = 100_000) -> None:
    import matplotlib.pyplot as plt

    qualities = [generate_potential() for _ in range(n)]

    print(f"min={min(qualities)}  max={max(qualities)}  mean={mean(qualities):.1f}")

    total_weight = sum(tier.weight for tier in TIERS)
    for tier in TIERS:
        count = sum(tier.low <= q <= tier.high for q in qualities)
        target = tier.weight / total_weight
        print(f"{tier.name:<15} actual {count / n:6.2%}   target {target:6.2%}")

    plt.hist(qualities, bins=[x - 0.5 for x in range(40, 101)], edgecolor="black")

    for tier in TIERS:
        plt.axvline(tier.low - 0.5, color="red", linestyle="--", alpha=0.4)

    plt.xlabel("Base quality (potential)")
    plt.ylabel("Number of players")
    plt.title(f"Base quality distribution ({n:,} players)")
    plt.tight_layout()
    plt.show()


def check_development_by_age(n_per_age: int = 5_000) -> None:
    import matplotlib.pyplot as plt

    ages = list(range(Player.MIN_AGE, 31))
    mean_overall: list[float] = []
    mean_potential: list[float] = []

    print(f"{'age':>3}  {'overall':>7}  {'potential':>9}  {'gap':>5}")
    for age in ages:
        players = [Player(age=age) for _ in range(n_per_age)]
        assert all(
            Player.MIN_OVERALL <= p.overall <= p.potential <= Player.MAX_OVERALL
            for p in players
        )

        overall = mean(p.overall for p in players)
        potential = mean(p.potential for p in players)
        mean_overall.append(overall)
        mean_potential.append(potential)
        print(
            f"{age:>3}  {overall:>7.1f}  {potential:>9.1f}  {potential - overall:>5.1f}"
        )

    plt.plot(ages, mean_potential, label="Mean potential")
    plt.plot(ages, mean_overall, label="Mean overall")
    plt.fill_between(ages, mean_overall, mean_potential, alpha=0.2)
    plt.xlabel("Age")
    plt.ylabel("Rating")
    plt.title(f"Overall vs potential by age ({n_per_age:,} players per age)")
    plt.legend()
    plt.tight_layout()
    plt.show()


def check_generated_player_attributes() -> None:
    for position in Position:
        print(f"\n\n========== POSITION: {position.abbreviation} ==========")
        for target in [40, 50, 60, 70, 80, 90, 99]:
            attributes = generate_attributes(position, target)
            rating = round(overall_rating(attributes, position))
            print(
                f"\n========== TARGET RATING: {target} | ACTUAL RATING: {rating} =========="
            )
            print(attributes)


CHECKS: dict[str, Callable[[], None]] = {
    "age": check_age_distribution,
    "base-quality": check_base_quality_distribution,
    "development": check_development_by_age,
    "attributes": check_generated_player_attributes,
}


# ========== COMMAND LINE ==========


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="football",
        description="Football simulation: example players and generation checks.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("demo", help="print a hand-made player and a random one")

    check = subparsers.add_parser("check", help="run a generation sanity check")
    check.add_argument("name", choices=sorted(CHECKS), help="which check to run")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "check":
        CHECKS[args.name]()
    else:
        show_example_players()


if __name__ == "__main__":
    main()
