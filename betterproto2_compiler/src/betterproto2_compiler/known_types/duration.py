import datetime
import re
import typing

import betterproto2

from betterproto2_compiler.lib.google.protobuf import Duration as VanillaDuration


class Duration(VanillaDuration):
    @classmethod
    def from_timedelta(cls, delta: datetime.timedelta) -> "Duration":
        total_ms = delta // datetime.timedelta(microseconds=1)
        seconds = int(total_ms / 1e6)
        nanos = int((total_ms % 1e6) * 1e3)
        return cls(seconds, nanos)

    def to_timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=self.seconds, microseconds=self.nanos / 1e3)

    @staticmethod
    def delta_to_json(delta: datetime.timedelta) -> str:
        parts = str(delta.total_seconds()).split(".")
        if len(parts) > 1:
            while len(parts[1]) not in (3, 6, 9):
                parts[1] = f"{parts[1]}0"
        return f"{'.'.join(parts)}s"

    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False):
        if isinstance(value, str):
            if not re.match(r"^-?\d+(\.\d+)?s$", value):
                raise ValueError(f"Invalid duration string: {value}")

            parts = value[:-1].split(".")

            seconds = int(parts[0])
            nanos = 0 if len(parts) == 1 else int(parts[1].ljust(9, "0")[:9])
            if seconds < 0:
                nanos = -nanos

            return Duration(seconds=seconds, nanos=nanos)

        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    # TODO typing
    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        # If the output format is PYTHON, we should have kept the wrapped type without building the real class
        assert output_format == betterproto2.OutputFormat.PROTO_JSON

        assert 0 <= self.nanos < 1e9

        if self.nanos == 0:
            return f"{self.seconds}s"

        nanos = f"{self.nanos:09d}".rstrip("0")
        if len(nanos) < 3:
            nanos += "0" * (3 - len(nanos))

        return f"{self.seconds}.{nanos}s"

    @staticmethod
    def from_wrapped(wrapped: datetime.timedelta) -> "Duration":
        return Duration.from_timedelta(wrapped)

    def to_wrapped(self) -> datetime.timedelta:
        return self.to_timedelta()
