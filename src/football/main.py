import argparse
from collections.abc import Callable
from dataclasses import astuple, fields
from statistics import mean, pstdev

from .aging import AGING_CLASS_OF, AgingClass
from .attributes import Attributes
from .development import gap_for
from .foot import Foot
from .generation import TIERS, generate_attributes, generate_potential
from .growth import expected_overall, grow_attributes
from .nationality import Nationality
from .player import Player
from .position import Position
from .ratings import PROFILES, overall_rating
from .value import VALUE_ANCHORS, base_value

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


def check_base_value_curve() -> None:
    import matplotlib.pyplot as plt

    ratings = list(range(Player.MIN_OVERALL, Player.MAX_OVERALL + 1))
    values = [base_value(rating) for rating in ratings]

    for rating, value in zip(ratings, values):
        print(f"{rating:>3}  €{value:>9,.0f}")

    plt.semilogy(ratings, values, label="Base value")
    plt.scatter(*zip(*VALUE_ANCHORS), color="red", zorder=3, label="Anchors")
    plt.xlabel("Rating")
    plt.ylabel("Value (log scale)")
    plt.title("Base value by rating")
    plt.legend()
    plt.tight_layout()
    plt.show()


CALIBRATION_RANGES: dict[int, tuple[int, int] | None] = {
    40: (5_000, 50_000),
    50: (30_000, 200_000),
    60: (150_000, 800_000),
    70: (1_000_000, 3_000_000),
    80: None,
    90: None,
}


def check_value_calibration(n: int = 200_000) -> None:
    players = [Player() for _ in range(n)]

    print(
        f"{'rating':>6}  {'players':>7}  {'p10':>11}  {'median':>11}  {'p90':>11}"
        f"  {'target range':<26}  fit"
    )
    for rating, target in CALIBRATION_RANGES.items():
        values = sorted(p.value for p in players if abs(p.overall - rating) <= 1)
        if len(values) < 20:
            print(f"{rating:>6}  {len(values):>7}  too few players")
            continue

        p10, median, p90 = (values[int(q * (len(values) - 1))] for q in (0.1, 0.5, 0.9))

        if target is None:
            target_text, fit = "none", "-"
        else:
            low, high = target
            target_text = f"€{low:,} to €{high:,}"
            notes = []
            if p10 < low:
                notes.append("p10 below range")
            if p90 > high:
                notes.append("p90 above range")
            fit = ", ".join(notes) or "inside"

        print(
            f"{rating:>6}  {len(values):>7,}  {p10:>11,}  {median:>11,}  {p90:>11,}"
            f"  {target_text:<26}  {fit}"
        )


def _class_skew(attributes: Attributes, position: Position) -> dict[AgingClass, float]:
    overall = overall_rating(attributes, position)
    weights = PROFILES[position]
    gaps: dict[AgingClass, list[float]] = {c: [] for c in AgingClass}

    for group in fields(Attributes):
        group_weights = getattr(weights, group.name)
        group_values = getattr(attributes, group.name)

        for attribute in fields(group_weights):
            if getattr(group_weights, attribute.name) > 0:
                aging_class = AGING_CLASS_OF[f"{group.name}.{attribute.name}"]
                gaps[aging_class].append(
                    getattr(group_values, attribute.name) - overall
                )

    return {c: mean(v) for c, v in gaps.items() if v}


def check_growth(n: int = 2_000) -> None:
    ages = list(range(Player.MIN_AGE, 28))
    overalls: dict[int, list[float]] = {age: [] for age in ages}
    curve: dict[int, list[float]] = {age: [] for age in ages}
    skews: dict[int, dict[AgingClass, list[float]]] = {
        age: {c: [] for c in AgingClass} for age in ages
    }

    for _ in range(n):
        player = Player(age=Player.MIN_AGE, development_offset=0.0)
        attributes = player.attributes

        for age in ages:
            overalls[age].append(overall_rating(attributes, player.position))
            curve[age].append(player.potential - gap_for(age, player.potential, 0.0))
            for aging_class, skew in _class_skew(attributes, player.position).items():
                skews[age][aging_class].append(skew)

            grown = grow_attributes(
                player.position, attributes, age, player.potential, 0.0
            )
            before = [v for group in astuple(attributes) for v in group]
            after = [v for group in astuple(grown) for v in group]
            assert all(b >= a for a, b in zip(before, after)), "an attribute decreased"
            attributes = grown

    print(
        f"{'age':>3}  {'overall':>7}  {'curve':>7}  {'spread':>6}  "
        + "  ".join(f"{c.name:>7}" for c in AgingClass)
    )
    for age in ages:
        diffs = [o - c for o, c in zip(overalls[age], curve[age])]
        cells = "  ".join(
            f"{mean(skews[age][c]):>7.1f}" if skews[age][c] else f"{'-':>7}"
            for c in AgingClass
        )
        print(
            f"{age:>3}  {mean(overalls[age]):>7.1f}  {mean(curve[age]):>7.1f}  "
            f"{pstdev(diffs):>6.2f}  {cells}"
        )


def _record_shape(
    player: Player,
    age: int,
    overalls: dict[int, list[float]],
    losses: dict[int, list[float]],
    skews: dict[int, dict[AgingClass, list[float]]],
) -> None:
    overalls[age].append(player.overall)
    losses[age].append(player.potential - player.overall)
    for aging_class, skew in _class_skew(player.attributes, player.position).items():
        skews[age][aging_class].append(skew)


def _print_shape_table(
    overalls: dict[int, list[float]],
    losses: dict[int, list[float]],
    skews: dict[int, dict[AgingClass, list[float]]],
) -> None:
    print(
        f"{'age':>3}  {'overall':>7}  {'below pot':>9}  "
        + "  ".join(f"{c.name:>7}" for c in AgingClass)
    )
    for age in overalls:  # noqa: PLC0206
        cells = "  ".join(
            f"{mean(skews[age][c]):>7.1f}" if skews[age][c] else f"{'-':>7}"
            for c in AgingClass
        )
        print(
            f"{age:>3}  {mean(overalls[age]):>7.1f}  {mean(losses[age]):>9.1f}  {cells}"
        )


def check_generated_shape(n: int = 1_000) -> None:
    ages = list(range(Player.MIN_AGE, 41))
    overalls = {age: [] for age in ages}
    losses = {age: [] for age in ages}
    skews = {age: {c: [] for c in AgingClass} for age in ages}

    for age in ages:
        for _ in range(n):
            player = Player(age=age, development_offset=0.0)
            _record_shape(player, age, overalls, losses, skews)

    _print_shape_table(overalls, losses, skews)


def check_career(n: int = 1_000) -> None:
    ages = list(range(Player.MIN_AGE, 41))
    overalls = {age: [] for age in ages}
    losses = {age: [] for age in ages}
    skews = {age: {c: [] for c in AgingClass} for age in ages}

    for _ in range(n):
        player = Player(age=Player.MIN_AGE, development_offset=0.0)
        for age in ages:
            _record_shape(player, age, overalls, losses, skews)
            if age != ages[-1]:
                player.advance_year()

    _print_shape_table(overalls, losses, skews)


def _empty_shape(
    ages: list[int],
) -> tuple[
    dict[int, list[float]],
    dict[int, list[float]],
    dict[int, dict[AgingClass, list[float]]],
]:
    return (
        {age: [] for age in ages},
        {age: [] for age in ages},
        {age: {c: [] for c in AgingClass} for age in ages},
    )


def check_offsets(n: int = 1_000) -> None:
    ages = list(range(Player.MIN_AGE, 41))

    for offset in (-3.0, 0.0, 3.0):
        career = _empty_shape(ages)
        generated = _empty_shape(ages)
        model: dict[int, list[float]] = {age: [] for age in ages}

        for _ in range(n):
            player = Player(age=Player.MIN_AGE, development_offset=offset)
            for age in ages:
                _record_shape(player, age, *career)
                model[age].append(
                    player.potential
                    - expected_overall(player.position, age, player.potential, offset)
                )
                if age != ages[-1]:
                    player.advance_year()

        for age in ages:
            for _ in range(n):
                _record_shape(
                    Player(age=age, development_offset=offset), age, *generated
                )

        _, career_loss, career_skew = career
        _, generated_loss, generated_skew = generated

        print(f"\noffset {offset:+.1f}")
        print("bp = below potential, F = FAST skew, M = MENTAL skew")
        print(
            f"{'age':>3}  {'bp_car':>7}  {'bp_gen':>7}  {'bp_mod':>7}  "
            f"{'F_car':>7}  {'F_gen':>7}  {'M_car':>7}  {'M_gen':>7}"
        )
        for age in ages:
            print(
                f"{age:>3}  {mean(career_loss[age]):>7.1f}  "
                f"{mean(generated_loss[age]):>7.1f}  {mean(model[age]):>7.1f}  "
                f"{mean(career_skew[age][AgingClass.FAST]):>7.1f}  "
                f"{mean(generated_skew[age][AgingClass.FAST]):>7.1f}  "
                f"{mean(career_skew[age][AgingClass.MENTAL]):>7.1f}  "
                f"{mean(generated_skew[age][AgingClass.MENTAL]):>7.1f}"
            )


CHECKS: dict[str, Callable[[], None]] = {
    "age": check_age_distribution,
    "base-quality": check_base_quality_distribution,
    "development": check_development_by_age,
    "attributes": check_generated_player_attributes,
    "value-curve": check_base_value_curve,
    "value-calibration": check_value_calibration,
    "growth": check_growth,
    "generated-shape": check_generated_shape,
    "career": check_career,
    "offsets": check_offsets,
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
