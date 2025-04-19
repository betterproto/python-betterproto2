from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from tests.output_betterproto.timestamp_dict_encode import Test

# Current World Timezone range (UTC-12 to UTC+14)
MIN_UTC_OFFSET_MIN = -12 * 60
MAX_UTC_OFFSET_MIN = 14 * 60

# Generate all timezones in range in 15 min increments
timezones = [timezone(timedelta(minutes=x)) for x in range(MIN_UTC_OFFSET_MIN, MAX_UTC_OFFSET_MIN + 1, 15)]


@pytest.mark.parametrize("tz", timezones)
def test_datetime_dict_encode(tz: timezone):
    original_time = datetime.now(tz=tz)
    original_message = Test()
    original_message.ts = original_time
    encoded = original_message.to_dict()
    decoded_message = Test.from_dict(encoded)

    # check that the timestamps are equal after decoding from dict
    assert original_message.ts.tzinfo is not None
    assert decoded_message.ts.tzinfo is not None
    assert original_message.ts == decoded_message.ts


@pytest.mark.parametrize("tz", timezones)
def test_json_serialize(tz: timezone):
    original_time = datetime.now(tz=tz)
    original_message = Test()
    original_message.ts = original_time
    json_serialized = original_message.to_json()
    decoded_message = Test.from_json(json_serialized)

    # check that the timestamps are equal after decoding from dict
    assert original_message.ts.tzinfo is not None
    assert decoded_message.ts.tzinfo is not None
    assert original_message.ts == decoded_message.ts
