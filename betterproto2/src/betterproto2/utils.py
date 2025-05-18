from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

T_co = TypeVar("T_co")
TT_co = TypeVar("TT_co", bound="type[Any]")


class classproperty(Generic[TT_co, T_co]):
    def __init__(self, func: Callable[[TT_co], T_co]):
        self.__func__ = func

    def __get__(self, instance: Any, type: TT_co) -> T_co:
        return self.__func__(type)


T = TypeVar("T")


def unwrap(x: T | None) -> T:
    """
    Unwraps an optional value, returning the value if it exists, or raises a ValueError if the value is None.

    Args:
        value (Optional[T]): The optional value to unwrap.

    Returns:
        T: The unwrapped value if it exists.

    Raises:
        ValueError: If the value is None.
    """
    if x is None:
        raise ValueError("Can't unwrap a None value")
    return x
