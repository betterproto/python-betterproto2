from datetime import (
    datetime,
    timezone,
)

import pytest

from betterproto2.nano_datetime import NanoDatetime
from tests.outputs.google.google.protobuf import Timestamp


@pytest.mark.parametrize(
    "dt",
    [
        datetime(2023, 10, 11, 9, 41, 12, tzinfo=timezone.utc),
        datetime.now(timezone.utc),
        # potential issue with floating point precision:
        datetime(2242, 12, 31, 23, 0, 0, 1, tzinfo=timezone.utc),
        # potential issue with negative timestamps:
        datetime(1969, 12, 31, 23, 0, 0, 1, tzinfo=timezone.utc),
    ],
)
def test_timestamp_to_datetime_and_back(dt: datetime):
    """
    Make sure converting a datetime to a protobuf timestamp message
    and then back again ends up with the same datetime.
    """
    assert Timestamp.from_datetime(dt).to_datetime() == dt


def test_invalid_datetime():
    """
    Make sure that a ValueError is raised when trying to convert a naive datetime
    to a protobuf timestamp message.
    """
    with pytest.raises(ValueError):
        Timestamp.from_datetime(datetime.now())


def test_timestamp_to_datetime_preserves_nanoseconds():
    ts = Timestamp(seconds=1, nanos=123456789)

    dt = ts.to_datetime()

    assert isinstance(dt, NanoDatetime)
    assert dt.microsecond == 123456
    assert dt.nanosecond_remainder == 789
    assert dt.total_nanoseconds == 123456789
    assert Timestamp.from_datetime(dt) == ts


def test_timestamp_to_datetime_preserves_negative_nanoseconds():
    ts = Timestamp(seconds=-1, nanos=999999999)

    dt = ts.to_datetime()

    assert isinstance(dt, NanoDatetime)
    assert dt == NanoDatetime(
        1969,
        12,
        31,
        23,
        59,
        59,
        999999,
        tzinfo=timezone.utc,
        nanosecond_remainder=999,
    )
    assert Timestamp.from_datetime(dt) == ts


def test_timestamp_dict_preserves_nanoseconds():
    ts = Timestamp.from_dict("1970-01-01T00:00:01.123456789Z")

    assert ts == Timestamp(seconds=1, nanos=123456789)
    assert ts.to_dict() == "1970-01-01T00:00:01.123456789Z"


def test_timestamp_dict_preserves_nanoseconds_with_offset():
    ts = Timestamp.from_dict("1970-01-01T01:00:01.123456789+01:00")

    assert ts == Timestamp(seconds=1, nanos=123456789)
    assert ts.to_dict() == "1970-01-01T00:00:01.123456789Z"
