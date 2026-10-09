from .nationality import Nationality

# import matplotlib.pyplot as plt
from .player import Player
from .position import Position


def main() -> None:
    # ========== CREATE AND EXAMINE HAND-CREATED AND RANDOM PLAYERS ==========
    p1 = Player(Nationality.UK, 16, Position.ATTACKING_MIDFIELDER)
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


if __name__ == "__main__":
    main()
