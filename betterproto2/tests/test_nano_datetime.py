from datetime import datetime, timezone

import pytest

from betterproto2.nano_datetime import NanoDatetime


@pytest.mark.parametrize("nanosecond_remainder", [-1, 1000])
def test_nanosecond_remainder_must_be_sub_microsecond(nanosecond_remainder: int) -> None:
    with pytest.raises(ValueError, match="nanosecond_remainder"):
        NanoDatetime(2024, 1, 2, tzinfo=timezone.utc, nanosecond_remainder=nanosecond_remainder)


def test_replace_preserves_nanosecond_remainder_by_default() -> None:
    dt = NanoDatetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc, nanosecond_remainder=789)

    replaced = dt.replace(second=6)

    assert replaced == NanoDatetime(
        2024,
        1,
        2,
        3,
        4,
        6,
        123456,
        tzinfo=timezone.utc,
        nanosecond_remainder=789,
    )


def test_replace_can_override_nanosecond_remainder() -> None:
    dt = NanoDatetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc, nanosecond_remainder=789)

    replaced = dt.replace(nanosecond_remainder=123)

    assert replaced.nanosecond_remainder == 123
    assert replaced.total_nanoseconds == 123456123


def test_equality_and_hash_include_nanosecond_remainder() -> None:
    base = datetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc)
    zero_remainder = NanoDatetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc)
    one_remainder = NanoDatetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc, nanosecond_remainder=1)
    two_remainder = NanoDatetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=timezone.utc, nanosecond_remainder=2)

    assert zero_remainder == base
    assert hash(zero_remainder) == hash(base)
    assert one_remainder != base
    assert one_remainder != two_remainder
    assert len({base, zero_remainder, one_remainder, two_remainder}) == 3


@pytest.mark.parametrize(
    ("dt", "expected"),
    [
        (NanoDatetime(1970, 1, 1, tzinfo=timezone.utc), "1970-01-01T00:00:00Z"),
        (NanoDatetime(1970, 1, 1, 0, 0, 0, 123000, tzinfo=timezone.utc), "1970-01-01T00:00:00.123Z"),
        (NanoDatetime(1970, 1, 1, 0, 0, 0, 123456, tzinfo=timezone.utc), "1970-01-01T00:00:00.123456Z"),
        (
            NanoDatetime(1970, 1, 1, 0, 0, 0, 123456, tzinfo=timezone.utc, nanosecond_remainder=789),
            "1970-01-01T00:00:00.123456789Z",
        ),
    ],
)
def test_to_json_uses_required_fraction_widths(dt: NanoDatetime, expected: str) -> None:
    assert NanoDatetime.to_json(dt) == expected


@pytest.mark.parametrize(
    ("value", "total_nanoseconds"),
    [
        ("1970-01-01T00:00:00.1Z", 100000000),
        ("1970-01-01T00:00:00.1234Z", 123400000),
        ("1970-01-01T00:00:00.12345678Z", 123456780),
        ("1970-01-01T00:00:00.123456789Z", 123456789),
    ],
)
def test_from_rfc3339_accepts_subsecond_fraction_widths(value: str, total_nanoseconds: int) -> None:
    dt = NanoDatetime.from_rfc3339(value)

    assert isinstance(dt, NanoDatetime)
    assert dt.total_nanoseconds == total_nanoseconds
