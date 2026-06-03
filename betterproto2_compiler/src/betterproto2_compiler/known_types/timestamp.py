import datetime
import typing

import betterproto2
from betterproto2.nano_datetime import NanoDatetime
from typing_extensions import Self

from betterproto2_compiler.lib.google.protobuf import Timestamp as VanillaTimestamp


class Timestamp(VanillaTimestamp):
    @classmethod
    def from_datetime(cls, dt: datetime.datetime) -> Self:
        seconds, nanos = NanoDatetime.to_timestamp(dt)
        return cls(seconds, nanos)

    def to_datetime(self) -> datetime.datetime:
        return NanoDatetime.from_timestamp(self.seconds, self.nanos)

    @staticmethod
    def timestamp_to_json(dt: datetime.datetime) -> str:
        return NanoDatetime.to_json(dt)

    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, str):
            return cls.from_datetime(NanoDatetime.from_rfc3339(value))

        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    # TODO typing
    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        # If the output format is PYTHON, we should have kept the wraped type without building the real class
        assert output_format == betterproto2.OutputFormat.PROTO_JSON

        return Timestamp.timestamp_to_json(self.to_datetime())

    @staticmethod
    def from_wrapped(wrapped: datetime.datetime) -> "Timestamp":
        return Timestamp.from_datetime(wrapped)

    def to_wrapped(self) -> datetime.datetime:
        return self.to_datetime()
