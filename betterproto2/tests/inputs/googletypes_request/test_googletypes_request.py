from datetime import datetime, timedelta

import pytest

import tests.outputs.googletypes_request.google.protobuf as protobuf
from tests.util import requires_grpclib  # noqa: F401


@pytest.mark.asyncio
async def test_channel_receives_wrapped_type(requires_grpclib):
    from tests.mocks import MockChannel
    from tests.outputs.googletypes_request.googletypes_request import Input, TestStub

    test_cases = [
        (TestStub.send_double, protobuf.DoubleValue, 2.5),
        (TestStub.send_float, protobuf.FloatValue, 2.5),
        (TestStub.send_int_64, protobuf.Int64Value, -64),
        (TestStub.send_u_int_64, protobuf.UInt64Value, 64),
        (TestStub.send_int_32, protobuf.Int32Value, -32),
        (TestStub.send_u_int_32, protobuf.UInt32Value, 32),
        (TestStub.send_bool, protobuf.BoolValue, True),
        (TestStub.send_string, protobuf.StringValue, "string"),
        (TestStub.send_bytes, protobuf.BytesValue, bytes(0xFF)[0:4]),
        (TestStub.send_datetime, protobuf.Timestamp, datetime(2038, 1, 19, 3, 14, 8)),
        (TestStub.send_timedelta, protobuf.Duration, timedelta(seconds=123456)),
    ]

    for service_method, wrapper_class, value in test_cases:
        wrapped_value = wrapper_class()
        wrapped_value.value = value
        channel = MockChannel(responses=[Input()])
        service = TestStub(channel)

        await service_method(service, wrapped_value)

        assert channel.requests[0]["request"] == type(wrapped_value)
