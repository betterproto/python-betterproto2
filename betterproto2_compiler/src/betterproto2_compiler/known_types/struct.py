import typing

import betterproto2
from typing_extensions import Self

from betterproto2_compiler.lib.google.protobuf import (
    ListValue as VanillaListValue,
    NullValue,
    Struct as VanillaStruct,
    Value as VanillaValue,
)


class Struct(VanillaStruct):
    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        assert isinstance(value, dict)

        fields: dict[str, Value] = {}

        for key, val in value.items():
            fields[key] = Value.from_dict(val)

        return cls(fields=fields)  # type: ignore[reportArgumentType]

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

        return {
            key: value.to_dict(
                output_format=output_format, casing=casing, include_default_values=include_default_values
            )
            for key, value in self.fields.items()
        }


# We can't use the unwrap mechanism to support directly using a Python object due to the None case: it would then be
# impossible to distinguish between the absence of the message and a None value.
class Value(VanillaValue):
    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        match value:
            case bool() as b:
                return cls(bool_value=b)
            case int() | float() as num:
                return cls(number_value=num)
            case str() as s:
                return cls(string_value=s)
            case list() as l:
                return cls(list_value=ListValue.from_dict(l))
            case dict() as d:
                return cls(struct_value=Struct.from_dict(d))
            case None:
                return cls(null_value=NullValue.NULL_VALUE)
        raise ValueError(f"Unknown value type: {type(value)}")

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

        match self:
            case Value(null_value=NullValue.NULL_VALUE):
                return None
            case Value(bool_value=bool(b)):
                return b
            case Value(number_value=int(num)) | Value(number_value=float(num)):
                return num
            case Value(string_value=str(s)):
                return s
            case Value(list_value=ListValue(values=l)):
                return [v.to_dict() for v in l]
            case Value(struct_value=Struct(fields=f)):
                return {k: v.to_dict() for k, v in f.items()}

        raise ValueError("Invalid value")


class ListValue(VanillaListValue):
    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        return cls(values=[Value.from_dict(v) for v in value])

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

        return [value.to_dict() for value in self.values]
