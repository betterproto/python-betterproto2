from __future__ import annotations

import datetime
import re
from typing import Any

import dateutil.parser
from typing_extensions import Self

_UTC = datetime.timezone.utc
_TIMESTAMP_ZERO = datetime.datetime(1970, 1, 1, tzinfo=_UTC)
_NANOS_PER_MICROSECOND = 1000
_MICROS_PER_SECOND = 10**6
_TIMESTAMP_RE = re.compile(
    r"^"
    r"(?P<date>\d{4}-\d{2}-\d{2})"
    r"T"
    r"(?P<time>\d{2}:\d{2}:\d{2})"
    r"(?:\.(?P<fraction>\d{1,9}))?"
    r"(?P<tz>Z|[+-]\d{2}:\d{2})"
    r"$"
)


class NanoDatetime(datetime.datetime):
    """A datetime that carries Timestamp sub-microsecond precision."""

    __slots__ = ("_nanosecond_remainder",)

    def __new__(
        cls,
        *args: Any,
        nanosecond_remainder: int = 0,
        **kwargs: Any,
    ) -> Self:
        if not 0 <= nanosecond_remainder < _NANOS_PER_MICROSECOND:
            raise ValueError("nanosecond_remainder must be in range 0..999")

        instance = super().__new__(cls, *args, **kwargs)
        object.__setattr__(instance, "_nanosecond_remainder", nanosecond_remainder)
        return instance

    @property
    def nanosecond_remainder(self) -> int:
        return getattr(self, "_nanosecond_remainder", 0)

    @property
    def total_nanoseconds(self) -> int:
        return self.microsecond * _NANOS_PER_MICROSECOND + self.nanosecond_remainder

    def replace(
        self, *args: Any, nanosecond_remainder: int | None = None, **kwargs: Any
    ) -> NanoDatetime:
        if nanosecond_remainder is None:
            nanosecond_remainder = self.nanosecond_remainder

        replaced = super().replace(*args, **kwargs)
        return _datetime_to_nano_datetime(replaced, nanosecond_remainder)

    def __repr__(self) -> str:
        base = super().__repr__()
        return f"{base[:-1]}, nanosecond_remainder={self.nanosecond_remainder})"

    def __eq__(self, other: Any) -> bool:
        equal = super().__eq__(other)
        if equal is NotImplemented or not isinstance(other, datetime.datetime):
            return equal

        return bool(equal) and self.nanosecond_remainder == _datetime_nanosecond_remainder(other)

    def __ne__(self, other: Any) -> bool:
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return equal

        return not equal

    def __hash__(self) -> int:
        if self.nanosecond_remainder == 0:
            return super().__hash__()

        return hash((super().__hash__(), self.nanosecond_remainder))

    @staticmethod
    def to_timestamp(dt: datetime.datetime) -> tuple[int, int]:
        if not dt.tzinfo:
            raise ValueError("datetime must be timezone aware")

        nanos = _datetime_total_nanoseconds(dt)
        dt = dt.astimezone(_UTC)

        offset = dt - _TIMESTAMP_ZERO
        offset_us = (offset.days * 24 * 60 * 60 + offset.seconds) * _MICROS_PER_SECOND + offset.microseconds
        seconds, _ = divmod(offset_us, _MICROS_PER_SECOND)
        return seconds, nanos

    @staticmethod
    def from_timestamp(seconds: int, nanos: int) -> NanoDatetime:
        micros, nanosecond_remainder = divmod(nanos, _NANOS_PER_MICROSECOND)
        offset = datetime.timedelta(seconds=seconds, microseconds=micros)
        dt = _TIMESTAMP_ZERO + offset
        return _datetime_to_nano_datetime(dt, nanosecond_remainder)

    @staticmethod
    def to_json(dt: datetime.datetime) -> str:
        seconds, nanos = NanoDatetime.to_timestamp(dt)
        dt = NanoDatetime.from_timestamp(seconds, nanos)
        result = dt.replace(microsecond=0, nanosecond_remainder=0, tzinfo=None).isoformat()

        if nanos == 0:
            return f"{result}Z"
        if nanos % 1_000_000 == 0:
            return f"{result}.{nanos // 1_000_000:03d}Z"
        if nanos % 1_000 == 0:
            return f"{result}.{nanos // 1_000:06d}Z"

        return f"{result}.{nanos:09d}Z"

    @staticmethod
    def from_rfc3339(value: str) -> datetime.datetime:
        match = _TIMESTAMP_RE.match(value)
        if match:
            tz = "+00:00" if match.group("tz") == "Z" else match.group("tz")
            dt = datetime.datetime.fromisoformat(f"{match.group('date')}T{match.group('time')}{tz}")

            fraction = (match.group("fraction") or "").ljust(9, "0")
            total_nanos = int(fraction) if fraction else 0
            micros, nanosecond_remainder = divmod(total_nanos, _NANOS_PER_MICROSECOND)

            dt = dt.replace(microsecond=micros).astimezone(_UTC)
            return _datetime_to_nano_datetime(dt, nanosecond_remainder)

        dt = dateutil.parser.isoparse(value)
        return dt.astimezone(_UTC)


def _datetime_nanosecond_remainder(dt: datetime.datetime) -> int:
    if isinstance(dt, NanoDatetime):
        return dt.nanosecond_remainder

    return 0


def _datetime_total_nanoseconds(dt: datetime.datetime) -> int:
    if isinstance(dt, NanoDatetime):
        return dt.total_nanoseconds

    return dt.microsecond * _NANOS_PER_MICROSECOND


def _datetime_to_nano_datetime(dt: datetime.datetime, nanosecond_remainder: int = 0) -> NanoDatetime:
    return NanoDatetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        tzinfo=dt.tzinfo,
        fold=dt.fold,
        nanosecond_remainder=nanosecond_remainder,
    )
