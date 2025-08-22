import typing

import betterproto2

from betterproto2_compiler.lib.google.protobuf import (
    ListValue as VanillaListValue,
    NullValue,
    Struct as VanillaStruct,
    Value as VanillaValue,
)


class Struct(VanillaStruct):
    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False):
        assert isinstance(value, dict)

        return cls(fields=value)

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

        return self.fields

    @staticmethod
    def from_wrapped(wrapped: betterproto2.JSON) -> "Struct":
        return Struct.from_dict(wrapped)

    def to_wrapped(self) -> betterproto2.JSON:
        return self.to_dict()


class Value(VanillaValue):
    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False):
        match value:
            case bool() as b:
                return cls(bool_value=b)
            case int() | float() as num:
                return cls(number_value=num)
            case str() as s:
                return cls(string_value=s)
            case list() as l:
                return cls(list_value=list(l))
            case dict() as d:
                return cls(struct_value=dict(d))
            case None:
                return cls(null_value=NullValue.NULL_VALUE)
            case _:
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

        return betterproto2.which_one_of(self, "kind")[1]

    @staticmethod
    def from_wrapped(wrapped: betterproto2.JSON) -> "Value":
        return Value.from_dict(wrapped)

    def to_wrapped(self) -> betterproto2.JSON:
        return self.to_dict()


class ListValue(VanillaListValue):
    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False):
        return cls(values=list(value))

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

        return self.values

    @staticmethod
    def from_wrapped(wrapped: list[betterproto2.JSON]) -> "ListValue":
        return ListValue.from_dict(wrapped)

    def to_wrapped(self) -> list[betterproto2.JSON]:
        return self.to_dict()
