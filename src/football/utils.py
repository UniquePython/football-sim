from collections.abc import Callable


def require_not_none[T](
    value: T | None,
    reason: str = "Unexpected None",
) -> T:
    if value is None:
        raise ValueError(reason)
    return value


def require_type[T](
    value: object,
    required_type: type[T],
    reason: str = "Unexpected type",
) -> T:
    if not isinstance(value, required_type) or (
        required_type is int and isinstance(value, bool)
    ):
        raise TypeError(
            f"{reason}: expected {required_type.__name__}, got {type(value).__name__}"
        )

    return value


def require_type_and_not_none[T](
    value: object,
    required_type: type[T],
    type_reason: str = "Unexpected value",
    none_reason: str = "Unexpected None",
) -> T:
    return require_type(
        require_not_none(value, none_reason), required_type, type_reason
    )


def require_condition[T](
    value: T,
    condition: Callable[[T], bool],
    reason: str = "Constraint violated",
) -> T:
    if not condition(value):
        raise ValueError(reason)

    return value


def value_or_default[T](
    value: T | None,
    default_factory: Callable[[], T],
) -> T:
    return value if value is not None else default_factory()
