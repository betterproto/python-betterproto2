import re
import typing

import betterproto2
from typing_extensions import Self

from betterproto2_compiler.lib.google.protobuf import FieldMask as VanillaFieldMask


class FieldMask(VanillaFieldMask):
    @staticmethod
    def _path_snake_to_camel(path: str) -> str:
        return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), path)

    @staticmethod
    def _path_camel_to_snake(path: str) -> str:
        return re.sub(r"([A-Z])", lambda m: "_" + m.group(1).lower(), path)

    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        if isinstance(value, str):
            paths = [FieldMask._path_camel_to_snake(p) for p in value.split(",") if p]
            return cls(paths=paths)
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
        return ",".join(FieldMask._path_snake_to_camel(p) for p in self.paths)
