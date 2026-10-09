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
    if not isinstance(value, required_type):
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
