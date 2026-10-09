from .nationality import Nationality
from .player import Player


def main() -> None:
    p1 = Player(Nationality.UK)
    p2 = Player.random()

    print(p1)
    print(p2)

    print(repr(p1))
    print(repr(p2))


if __name__ == "__main__":
    main()
