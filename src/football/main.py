import matplotlib.pyplot as plt

from .generation import TIERS, generate_attributes, generate_base_quality
from .nationality import Nationality
from .player import Player
from .position import Position
from .ratings import overall_rating


def check_base_quality_distribution(n: int = 100_000) -> None:
    qualities = [generate_base_quality() for _ in range(n)]

    print(f"min={min(qualities)}  max={max(qualities)}  mean={sum(qualities) / n:.1f}")

    total_weight = sum(tier.weight for tier in TIERS)
    for tier in TIERS:
        count = sum(tier.low <= q <= tier.high for q in qualities)
        target = tier.weight / total_weight
        print(f"{tier.name:<15} actual {count / n:6.2%}   target {target:6.2%}")

    # Half-integer edges so each integer rating gets its own centred bar
    plt.hist(qualities, bins=[x - 0.5 for x in range(40, 101)], edgecolor="black")

    # Mark the tier boundaries so the comb is easy to see
    for tier in TIERS:
        plt.axvline(tier.low - 0.5, color="red", linestyle="--", alpha=0.4)

    plt.xlabel("Base quality")
    plt.ylabel("Number of players")
    plt.title(f"Base quality distribution ({n:,} players)")
    plt.tight_layout()
    plt.show()


def check_generated_player_attributes() -> None:
    for position in list(Position):
        print(f"\n\n========== POSITION: {position.abbreviation} ==========")
        for target in [40, 50, 60, 70, 80, 90, 99]:
            attributes = generate_attributes(position, target)
            rating = round(overall_rating(attributes, position))
            print(
                f"\n========== TARGET RATING: {target} | ACTUAL RATING: {rating} =========="
            )
            print(attributes)


def main() -> None:
    # ========== CREATE AND EXAMINE HAND-CREATED AND RANDOM PLAYERS ==========
    p1 = Player(Nationality.UK, 16, Position.ATTACKING_MIDFIELDER, 69)
    p2 = Player()

    print(p1)
    print(p2)

    print(repr(p1))
    print(repr(p2))

    # ========== CHECK AGE DISTRIBUTION ==========
    # ages = [Player().age for _ in range(10_000)]
    # plt.hist(
    #     ages,
    #     bins=range(15, 44),
    #     edgecolor="black",
    # )
    # plt.xlabel("Player age")
    # plt.ylabel("Number of players")
    # plt.title("Distribution of Football Player Ages")
    # plt.xticks(range(16, 43))
    # plt.tight_layout()
    # plt.show()

    # check_base_quality_distribution()

    # check_generated_player_attributes()


if __name__ == "__main__":
    main()
