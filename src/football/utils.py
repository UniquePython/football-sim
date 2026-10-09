def require_not_none[T](
    value: T | None,
    reason: str = "Unexpected None",
) -> T:
    if value is None:
        raise ValueError(reason)
    return value


def require_type[M, N](
    value: M | None,
    required_type: type[N],
    reason: str = "Unexpected type",
) -> N:
    value = require_not_none(value, reason)

    if not isinstance(value, required_type):
        raise TypeError(
            f"{reason}: expected {required_type.__name__}, got {type(value).__name__}"
        )

    return value
