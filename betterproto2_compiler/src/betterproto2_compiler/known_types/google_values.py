import typing

import betterproto2
from typing_extensions import Self

from betterproto2_compiler.lib.google.protobuf import (
    BoolValue as VanillaBoolValue,
    BytesValue as VanillaBytesValue,
    DoubleValue as VanillaDoubleValue,
    FloatValue as VanillaFloatValue,
    Int32Value as VanillaInt32Value,
    Int64Value as VanillaInt64Value,
    StringValue as VanillaStringValue,
    UInt32Value as VanillaUInt32Value,
    UInt64Value as VanillaUInt64Value,
)


class BoolValue(VanillaBoolValue):
    @staticmethod
    def from_wrapped(wrapped: bool) -> "BoolValue":
        return BoolValue(value=wrapped)

    def to_wrapped(self) -> bool:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, bool):
            return BoolValue(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class Int32Value(VanillaInt32Value):
    @staticmethod
    def from_wrapped(wrapped: int) -> "Int32Value":
        return Int32Value(value=wrapped)

    def to_wrapped(self) -> int:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, int):
            return Int32Value(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class Int64Value(VanillaInt64Value):
    @staticmethod
    def from_wrapped(wrapped: int) -> "Int64Value":
        return Int64Value(value=wrapped)

    def to_wrapped(self) -> int:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, int):
            return Int64Value(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class UInt32Value(VanillaUInt32Value):
    @staticmethod
    def from_wrapped(wrapped: int) -> "UInt32Value":
        return UInt32Value(value=wrapped)

    def to_wrapped(self) -> int:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, int):
            return UInt32Value(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class UInt64Value(VanillaUInt64Value):
    @staticmethod
    def from_wrapped(wrapped: int) -> "UInt64Value":
        return UInt64Value(value=wrapped)

    def to_wrapped(self) -> int:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, int):
            return UInt64Value(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class FloatValue(VanillaFloatValue):
    @staticmethod
    def from_wrapped(wrapped: float) -> "FloatValue":
        return FloatValue(value=wrapped)

    def to_wrapped(self) -> float:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, float):
            return FloatValue(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class DoubleValue(VanillaDoubleValue):
    @staticmethod
    def from_wrapped(wrapped: float) -> "DoubleValue":
        return DoubleValue(value=wrapped)

    def to_wrapped(self) -> float:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, float):
            return DoubleValue(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class StringValue(VanillaStringValue):
    @staticmethod
    def from_wrapped(wrapped: str) -> "StringValue":
        return StringValue(value=wrapped)

    def to_wrapped(self) -> str:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, str):
            return StringValue(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value


class BytesValue(VanillaBytesValue):
    @staticmethod
    def from_wrapped(wrapped: bytes) -> "BytesValue":
        return BytesValue(value=wrapped)

    def to_wrapped(self) -> bytes:
        return self.value

    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, bytes):
            return BytesValue(value=value)
        return super().from_dict(value, ignore_unknown_fields=ignore_unknown_fields)

    def to_dict(
        self,
        *,
        output_format: betterproto2.OutputFormat = betterproto2.OutputFormat.PROTO_JSON,
        casing: betterproto2.Casing = betterproto2.Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, typing.Any] | typing.Any:
        return self.value
