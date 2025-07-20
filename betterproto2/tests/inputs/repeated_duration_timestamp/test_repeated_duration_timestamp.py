from datetime import datetime, timedelta

from tests.outputs.repeated_duration_timestamp.repeated_duration_timestamp import Test


def test_roundtrip():
    message = Test()
    message.times = [datetime.now(), datetime.now()]
    message.durations = [timedelta(), timedelta()]
