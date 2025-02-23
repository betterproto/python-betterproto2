import pytest

import betterproto2


class Colour(betterproto2.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


PURPLE = Colour(4)


@pytest.mark.parametrize(
    "member, str_value",
    [
        (Colour.RED, "RED"),
        (Colour.GREEN, "GREEN"),
        (Colour.BLUE, "BLUE"),
        (PURPLE, "UNKNOWN(4)"),
    ],
)
def test_str(member: Colour, str_value: str) -> None:
    assert str(member) == str_value


@pytest.mark.parametrize(
    "member, repr_value",
    [
        (Colour.RED, "<Colour.RED: 1>"),
        (Colour.GREEN, "<Colour.GREEN: 2>"),
        (Colour.BLUE, "<Colour.BLUE: 3>"),
        (PURPLE, "<Colour.~UNKNOWN: 4>"),
    ],
)
def test_repr(member: Colour, repr_value: str) -> None:
    assert repr(member) == repr_value


@pytest.mark.parametrize(
    "member, values",
    [
        (Colour.RED, ("RED", 1)),
        (Colour.GREEN, ("GREEN", 2)),
        (Colour.BLUE, ("BLUE", 3)),
        (PURPLE, ("", 4)),
    ],
)
def test_name_values(member: Colour, values: tuple[str | None, int]) -> None:
    assert (member.name, member.value) == values


@pytest.mark.parametrize(
    "member, input_str",
    [
        (Colour.RED, "RED"),
        (Colour.GREEN, "GREEN"),
        (Colour.BLUE, "BLUE"),
    ],
)
def test_from_string(member: Colour, input_str: str) -> None:
    assert Colour.from_string(input_str) == member


@pytest.mark.parametrize(
    "member, input_int",
    [
        (Colour.RED, 1),
        (Colour.GREEN, 2),
        (Colour.BLUE, 3),
        (PURPLE, 4),
    ],
)
def test_construction(member: Colour, input_int: int) -> None:
    assert Colour(input_int) == member
