from __future__ import annotations

__all__ = ["__version__", "check_compiler_version", "classproperty", "unwrap", "MessagePool", "validators"]

import dataclasses
import enum as builtin_enum
import json
import math
import struct
import sys
import warnings
from abc import ABC
from base64 import b64decode, b64encode
from collections.abc import Callable, Generator, Iterable, Mapping
from copy import deepcopy
from enum import IntEnum
from io import BytesIO
from itertools import count
from typing import TYPE_CHECKING, Any, ClassVar, get_type_hints

from typing_extensions import Self

try:
    import pydantic
    import pydantic_core
except ImportError:
    pydantic = None
    pydantic_core = None

import betterproto2.validators as validators
from betterproto2.message_pool import MessagePool
from betterproto2.utils import unwrap

from ._types import T
from ._version import __version__, check_compiler_version
from .casing import camel_case, safe_snake_case, snake_case
from .enum import Enum as Enum
from .grpc.grpclib_client import ServiceStub as ServiceStub
from .utils import classproperty

if TYPE_CHECKING:
    from _typeshed import SupportsRead, SupportsWrite

# Proto 3 data types
TYPE_ENUM = "enum"
TYPE_BOOL = "bool"
TYPE_INT32 = "int32"
TYPE_INT64 = "int64"
TYPE_UINT32 = "uint32"
TYPE_UINT64 = "uint64"
TYPE_SINT32 = "sint32"
TYPE_SINT64 = "sint64"
TYPE_FLOAT = "float"
TYPE_DOUBLE = "double"
TYPE_FIXED32 = "fixed32"
TYPE_SFIXED32 = "sfixed32"
TYPE_FIXED64 = "fixed64"
TYPE_SFIXED64 = "sfixed64"
TYPE_STRING = "string"
TYPE_BYTES = "bytes"
TYPE_MESSAGE = "message"
TYPE_MAP = "map"

# Fields that use a fixed amount of space (4 or 8 bytes)
FIXED_TYPES = [
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_FIXED32,
    TYPE_SFIXED32,
    TYPE_FIXED64,
    TYPE_SFIXED64,
]

# Fields that are numerical 64-bit types
INT_64_TYPES = [TYPE_INT64, TYPE_UINT64, TYPE_SINT64, TYPE_FIXED64, TYPE_SFIXED64]

# Fields that are numerical 32-bit types
INT_32_TYPES = [TYPE_INT32, TYPE_UINT32, TYPE_SINT32, TYPE_FIXED32, TYPE_SFIXED32]

# Fields that are numerical types
ALL_INT_TYPES = INT_64_TYPES + INT_32_TYPES

# Fields that are efficiently packed when
PACKED_TYPES = [
    TYPE_ENUM,
    TYPE_BOOL,
    TYPE_INT32,
    TYPE_INT64,
    TYPE_UINT32,
    TYPE_UINT64,
    TYPE_SINT32,
    TYPE_SINT64,
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_FIXED32,
    TYPE_SFIXED32,
    TYPE_FIXED64,
    TYPE_SFIXED64,
]

# Wire types
# https://developers.google.com/protocol-buffers/docs/encoding#structure
WIRE_VARINT = 0
WIRE_FIXED_64 = 1
WIRE_LEN_DELIM = 2
WIRE_FIXED_32 = 5

# Mappings of which Proto 3 types correspond to which wire types.
WIRE_VARINT_TYPES = [
    TYPE_ENUM,
    TYPE_BOOL,
    TYPE_INT32,
    TYPE_INT64,
    TYPE_UINT32,
    TYPE_UINT64,
    TYPE_SINT32,
    TYPE_SINT64,
]

WIRE_FIXED_32_TYPES = [TYPE_FLOAT, TYPE_FIXED32, TYPE_SFIXED32]
WIRE_FIXED_64_TYPES = [TYPE_DOUBLE, TYPE_FIXED64, TYPE_SFIXED64]
WIRE_LEN_DELIM_TYPES = [TYPE_STRING, TYPE_BYTES, TYPE_MESSAGE, TYPE_MAP]

# Indicator of message delimitation in streams
SIZE_DELIMITED = -1


# Special protobuf json doubles
INFINITY = "Infinity"
NEG_INFINITY = "-Infinity"
NAN = "NaN"


class Casing(builtin_enum.Enum):
    """Casing constants for serialization."""

    CAMEL = 1
    SNAKE = 2

    def __call__(self, name: str) -> str:
        """Convert the given name to the casing style."""
        if self == Casing.CAMEL:
            return camel_case(name)
        elif self == Casing.SNAKE:
            return snake_case(name)
        else:
            raise ValueError(f"Unknown casing style: {self}")


@dataclasses.dataclass(frozen=True)
class FieldMetadata:
    """Stores internal metadata used for parsing & serialization."""

    # Protobuf field number
    number: int
    # Protobuf type name
    proto_type: str

    # Map information if the proto_type is a map
    map_meta: tuple[FieldMetadata, FieldMetadata] | None = None

    # Groups several "one-of" fields together
    group: str | None = None

    # When a message is wrapped, the original message (BoolValue, Timestamp, ...)
    unwrap: Callable[[], type] | None = None

    # Is the field optional
    optional: bool | None = False
    # Is the field repeated
    repeated: bool | None = False

    @staticmethod
    def get(field: dataclasses.Field) -> FieldMetadata:
        """Returns the field metadata for a dataclass field."""
        return field.metadata["betterproto"]


def map_meta(
    proto_type_1: str,
    proto_type_2: str,
    *,
    unwrap_2: Callable[[], type] | None = None,
) -> tuple[FieldMetadata, FieldMetadata]:
    key_meta = FieldMetadata(1, proto_type_1)
    value_meta = FieldMetadata(2, proto_type_2, unwrap=unwrap_2)

    return key_meta, value_meta


def field(
    number: int,
    proto_type: str,
    *,
    default_factory: Callable[[], Any] | None = None,
    map_meta: tuple[FieldMetadata, FieldMetadata] | None = None,
    group: str | None = None,
    unwrap: Callable[[], type] | None = None,
    optional: bool = False,
    repeated: bool = False,
) -> Any:  # Return type is Any to pass type checking
    """Creates a dataclass field with attached protobuf metadata."""
    if repeated:
        default_factory = list

    elif optional or group:
        default_factory = type(None)

    else:
        default_factory = {
            TYPE_ENUM: default_factory,
            TYPE_BOOL: bool,
            TYPE_INT32: int,
            TYPE_INT64: int,
            TYPE_UINT32: int,
            TYPE_UINT64: int,
            TYPE_SINT32: int,
            TYPE_SINT64: int,
            TYPE_FLOAT: float,
            TYPE_DOUBLE: float,
            TYPE_FIXED32: int,
            TYPE_SFIXED32: int,
            TYPE_FIXED64: int,
            TYPE_SFIXED64: int,
            TYPE_STRING: str,
            TYPE_BYTES: bytes,
            TYPE_MESSAGE: type(None),
            TYPE_MAP: dict,
        }[proto_type]

    return dataclasses.field(
        default_factory=default_factory or dataclasses.MISSING,
        metadata={"betterproto": FieldMetadata(number, proto_type, map_meta, group, unwrap, optional, repeated)},
    )


def _pack_fmt(proto_type: str) -> str:
    """Returns a little-endian format string for reading/writing binary."""
    return {
        TYPE_DOUBLE: "<d",
        TYPE_FLOAT: "<f",
        TYPE_FIXED32: "<I",
        TYPE_FIXED64: "<Q",
        TYPE_SFIXED32: "<i",
        TYPE_SFIXED64: "<q",
    }[proto_type]


def dump_varint(value: int, stream: SupportsWrite[bytes]) -> None:
    """Encodes a single varint and dumps it into the provided stream."""
    if value < -(1 << 63):
        raise ValueError(
            "Negative value is not representable as a 64-bit integer - unable to encode a varint within 10 bytes."
        )
    elif value < 0:
        value += 1 << 64

    bits = value & 0x7F
    value >>= 7
    while value:
        stream.write((0x80 | bits).to_bytes(1, "little"))
        bits = value & 0x7F
        value >>= 7
    stream.write(bits.to_bytes(1, "little"))


def encode_varint(value: int) -> bytes:
    """Encodes a single varint value for serialization."""
    with BytesIO() as stream:
        dump_varint(value, stream)
        return stream.getvalue()


def _preprocess_single(proto_type: str, unwrap: Callable[[], type] | None, value: Any) -> bytes:
    """Adjusts values before serialization."""
    if proto_type in (
        TYPE_ENUM,
        TYPE_BOOL,
        TYPE_INT32,
        TYPE_INT64,
        TYPE_UINT32,
        TYPE_UINT64,
    ):
        return encode_varint(value)
    elif proto_type in (TYPE_SINT32, TYPE_SINT64):
        # Handle zig-zag encoding.
        return encode_varint(value << 1 if value >= 0 else (value << 1) ^ (~0))
    elif proto_type in FIXED_TYPES:
        return struct.pack(_pack_fmt(proto_type), value)
    elif proto_type == TYPE_STRING:
        return value.encode("utf-8")
    elif proto_type == TYPE_MESSAGE:
        if unwrap is not None:
            value = unwrap().from_wrapped(value)

        return bytes(value)

    return value


def _serialize_single(
    field_number: int,
    proto_type: str,
    value: Any,
    *,
    unwrap: Callable[[], type] | None = None,
) -> bytes:
    """Serializes a single field and value."""
    value = _preprocess_single(proto_type, unwrap, value)

    output = bytearray()
    if proto_type in WIRE_VARINT_TYPES:
        key = encode_varint(field_number << 3)
        output += key + value
    elif proto_type in WIRE_FIXED_32_TYPES:
        key = encode_varint((field_number << 3) | 5)
        output += key + value
    elif proto_type in WIRE_FIXED_64_TYPES:
        key = encode_varint((field_number << 3) | 1)
        output += key + value
    elif proto_type in WIRE_LEN_DELIM_TYPES:
        key = encode_varint((field_number << 3) | 2)
        output += key + encode_varint(len(value)) + value
    else:
        raise NotImplementedError(proto_type)

    return bytes(output)


def _parse_float(value: Any) -> float:
    """Parse the given value to a float

    Parameters
    ----------
    value: Any
        Value to parse

    Returns
    -------
    float
        Parsed value
    """
    if value == INFINITY:
        return float("inf")
    if value == NEG_INFINITY:
        return -float("inf")
    if value == NAN:
        return float("nan")
    return float(value)


def _dump_float(value: float) -> float | str:
    """Dump the given float to JSON

    Parameters
    ----------
    value: float
        Value to dump

    Returns
    -------
    Union[float, str]
        Dumped value, either a float or the strings
    """
    if value == float("inf"):
        return INFINITY
    if value == -float("inf"):
        return NEG_INFINITY
    if isinstance(value, float) and math.isnan(value):
        return NAN
    return value


def load_varint(stream: SupportsRead[bytes]) -> tuple[int, bytes]:
    """
    Load a single varint value from a stream. Returns the value and the raw bytes read.
    """
    result = 0
    raw = b""
    for shift in count(0, 7):
        if shift >= 64:
            break
        b = stream.read(1)
        if not b:
            raise EOFError("Stream ended unexpectedly while attempting to load varint.")
        raw += b
        b_int = int.from_bytes(b, byteorder="little")
        result |= (b_int & 0x7F) << shift
        if not (b_int & 0x80):
            return result, raw

    raise ValueError("Too many bytes when decoding varint.")


def decode_varint(buffer: bytes, pos: int) -> tuple[int, int]:
    """
    Decode a single varint value from a byte buffer. Returns the value and the
    new position in the buffer.
    """
    with BytesIO(buffer) as stream:
        stream.seek(pos)
        value, raw = load_varint(stream)
    return value, pos + len(raw)


@dataclasses.dataclass(frozen=True)
class ParsedField:
    number: int
    wire_type: int
    value: Any
    raw: bytes


def load_fields(stream: SupportsRead[bytes]) -> Generator[ParsedField, None, None]:
    while True:
        try:
            num_wire, raw = load_varint(stream)
        except EOFError:
            return
        number = num_wire >> 3
        wire_type = num_wire & 0x7

        decoded: Any = None
        if wire_type == WIRE_VARINT:
            decoded, r = load_varint(stream)
            raw += r
        elif wire_type == WIRE_FIXED_64:
            decoded = stream.read(8)
            raw += decoded
        elif wire_type == WIRE_LEN_DELIM:
            length, r = load_varint(stream)
            decoded = stream.read(length)
            raw += r
            raw += decoded
        elif wire_type == WIRE_FIXED_32:
            decoded = stream.read(4)
            raw += decoded

        yield ParsedField(number=number, wire_type=wire_type, value=decoded, raw=raw)


def parse_fields(value: bytes) -> Generator[ParsedField, None, None]:
    i = 0
    while i < len(value):
        start = i
        num_wire, i = decode_varint(value, i)
        number = num_wire >> 3
        wire_type = num_wire & 0x7

        decoded: Any = None
        if wire_type == WIRE_VARINT:
            decoded, i = decode_varint(value, i)
        elif wire_type == WIRE_FIXED_64:
            decoded, i = value[i : i + 8], i + 8
        elif wire_type == WIRE_LEN_DELIM:
            length, i = decode_varint(value, i)
            decoded = value[i : i + length]
            i += length
        elif wire_type == WIRE_FIXED_32:
            decoded, i = value[i : i + 4], i + 4

        yield ParsedField(number=number, wire_type=wire_type, value=decoded, raw=value[start:i])


class ProtoClassMetadata:
    __slots__ = (
        "oneof_field_by_group",
        "default_gen",
        "cls_by_field",
        "field_name_by_number",
        "meta_by_field_name",
        "sorted_field_names",
    )

    oneof_field_by_group: dict[str, set[dataclasses.Field]]
    field_name_by_number: dict[int, str]
    meta_by_field_name: dict[str, FieldMetadata]
    sorted_field_names: tuple[str, ...]
    default_gen: dict[str, Callable[[], Any]]
    cls_by_field: dict[str, type]

    def __init__(self, cls: type[Message]):
        by_group: dict[str, set] = {}
        by_field_name = {}
        by_field_number = {}

        assert dataclasses.is_dataclass(cls)
        fields = dataclasses.fields(cls)
        for field in fields:
            meta = FieldMetadata.get(field)

            if meta.group:
                by_group.setdefault(meta.group, set()).add(field)

            by_field_name[field.name] = meta
            by_field_number[meta.number] = field.name

        self.oneof_field_by_group = by_group
        self.field_name_by_number = by_field_number
        self.meta_by_field_name = by_field_name
        self.sorted_field_names = tuple(by_field_number[number] for number in sorted(by_field_number))

        self.default_gen = {}
        for field in fields:
            assert field.default_factory is not dataclasses.MISSING
            self.default_gen[field.name] = field.default_factory

        self.cls_by_field = self._get_cls_by_field(cls, fields)

    @staticmethod
    def _get_cls_by_field(cls: type[Message], fields: Iterable[dataclasses.Field]) -> dict[str, type]:  # type: ignore[reportSelfClsParameterName]
        field_cls = {}

        for field_ in fields:
            meta = FieldMetadata.get(field_)
            if meta.proto_type == TYPE_MAP:
                assert meta.map_meta
                kt = cls._cls_for(field_, index=0)
                vt = cls._cls_for(field_, index=1)

                if meta.map_meta[1].proto_type == TYPE_ENUM:
                    value_field = field(2, meta.map_meta[1].proto_type, default_factory=lambda: vt(0))
                else:
                    value_field = field(2, meta.map_meta[1].proto_type, unwrap=meta.map_meta[1].unwrap)

                field_cls[field_.name] = dataclasses.make_dataclass(
                    "Entry",
                    [
                        ("key", kt, field(1, meta.map_meta[0].proto_type)),
                        ("value", vt, value_field),
                    ],
                    bases=(Message,),
                )
                field_cls[f"{field_.name}.value"] = vt
            else:
                field_cls[field_.name] = cls._cls_for(field_)

        return field_cls


class OutputFormat(IntEnum):
    """
    Chosen output format for the `Message.to_dict` method.
    """

    PYTHON = 1
    PROTO_JSON = 2


def _value_to_dict(
    value: Any,
    proto_type: str,
    field_type: type,
    unwrapped_type: Callable[[], type] | None,
    output_format: OutputFormat,
    casing: Casing,
    include_default_values: bool,
) -> tuple[Any, bool]:
    """
    Convert a single item to a Python dictionnary. This function is called on each element of a
    list, set, etc by `Message.to_dict`.

    Returns:
        A tuple (dict, is_default_value)
    """
    kwargs = {  # For recursive calls
        "output_format": output_format,
        "casing": casing,
        "include_default_values": include_default_values,
    }

    if proto_type == TYPE_MESSAGE:
        if unwrapped_type is not None and output_format == OutputFormat.PYTHON:
            return value, False

        if unwrapped_type is not None:
            value = unwrapped_type().from_wrapped(value)

        return value.to_dict(**kwargs), False

    if output_format == OutputFormat.PYTHON:
        return value, not bool(value)

    # PROTO_JSON
    if proto_type in INT_64_TYPES:
        return str(value), not bool(value)
    if proto_type == TYPE_BYTES:
        return b64encode(value).decode("utf8"), not (bool(value))
    if proto_type == TYPE_ENUM:
        return field_type(value).name, not bool(value)
    if proto_type in (TYPE_FLOAT, TYPE_DOUBLE):
        return _dump_float(value), not bool(value)
    return value, not bool(value)


def _value_from_dict(value: Any, meta: FieldMetadata, field_type: type) -> Any:
    if meta.proto_type == TYPE_MESSAGE:
        msg_cls = meta.unwrap() if meta.unwrap else field_type

        msg = msg_cls.from_dict(value)

        if meta.unwrap:
            return msg.to_wrapped()
        return msg

    if meta.proto_type == TYPE_ENUM:
        if isinstance(value, str):
            return field_type.from_string(value)
        if isinstance(value, int):
            return field_type(value)
        if isinstance(value, Enum):
            return value
        raise ValueError("Enum value must be a string or an Enum instance")

    if meta.proto_type in ALL_INT_TYPES:
        return int(value)

    if meta.proto_type == TYPE_BYTES:
        return b64decode(value)

    if meta.proto_type in (TYPE_FLOAT, TYPE_DOUBLE):
        return _parse_float(value)

    return value


class Message(ABC):
    """
    The base class for protobuf messages, all generated messages will inherit from
    it. This class registers the message fields which are used by the serializers and
    parsers to go between the Python, binary and JSON representations of the message.
    """

    _unknown_fields: bytes
    _betterproto_meta: ClassVar[ProtoClassMetadata]

    def __post_init__(self) -> None:
        self._unknown_fields = b""

    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        for field_name in self._betterproto.meta_by_field_name:
            self_val = self.__getattribute__(field_name)
            other_val = other.__getattribute__(field_name)

            if self_val != other_val:
                # We consider two nan values to be the same for the
                # purposes of comparing messages (otherwise a message
                # is not equal to itself)
                if (
                    isinstance(self_val, float)
                    and isinstance(other_val, float)
                    and math.isnan(self_val)
                    and math.isnan(other_val)
                ):
                    continue
                else:
                    return False

        return True

    def __repr__(self) -> str:
        parts = [
            f"{field_name}={value!r}"
            for field_name in self._betterproto.sorted_field_names
            for value in (self.__getattribute__(field_name),)
            if value != self._get_field_default(field_name)
        ]
        return f"{self.__class__.__name__}({', '.join(parts)})"

    def __bool__(self) -> bool:
        """True if the message has any fields with non-default values."""
        return any(
            self.__getattribute__(field_name) != self._get_field_default(field_name)
            for field_name in self._betterproto.meta_by_field_name
        )

    def __deepcopy__(self: T, _: Any = {}) -> T:
        kwargs = {}
        for name in self._betterproto.sorted_field_names:
            value = self.__getattribute__(name)
            kwargs[name] = deepcopy(value)
        return self.__class__(**kwargs)  # type: ignore

    def __copy__(self: T, _: Any = {}) -> T:
        kwargs = {}
        for name in self._betterproto.sorted_field_names:
            value = self.__getattribute__(name)
            kwargs[name] = value
        return self.__class__(**kwargs)  # type: ignore

    @classproperty
    def _betterproto(cls: type[Self]) -> ProtoClassMetadata:  # type: ignore
        """
        Lazy initialize metadata for each protobuf class.
        It may be initialized multiple times in a multi-threaded environment,
        but that won't affect the correctness.
        """
        try:
            return cls._betterproto_meta
        except AttributeError:
            cls._betterproto_meta = ProtoClassMetadata(cls)
            return cls._betterproto_meta

    def _is_pydantic(self) -> bool:
        """
        Check if the message is a pydantic dataclass.
        """
        return pydantic is not None and pydantic.dataclasses.is_pydantic_dataclass(type(self))

    def _validate(self) -> None:
        """
        Manually validate the message using pydantic.

        This is useful since pydantic does not revalidate the message when fields are changed. This function doesn't
        validate the fields recursively.
        """
        if not self._is_pydantic():
            raise TypeError("Validation is only available for pydantic dataclasses.")

        dict = self.__dict__.copy()
        del dict["_unknown_fields"]
        pydantic_core.SchemaValidator(self.__pydantic_core_schema__).validate_python(dict)  # type: ignore

    def dump(self, stream: SupportsWrite[bytes], delimit: bool = False) -> None:
        """
        Dumps the binary encoded Protobuf message to the stream.

        Parameters
        -----------
        stream: :class:`BinaryIO`
            The stream to dump the message to.
        delimit:
            Whether to prefix the message with a varint declaring its size.
            TODO is it actually needed?
        """
        b = bytes(self)

        if delimit:
            dump_varint(len(b), stream)

        stream.write(b)

    def __bytes__(self) -> bytes:
        """
        Get the binary encoded Protobuf representation of this message instance.
        """
        if self._is_pydantic():
            self._validate()

        with BytesIO() as stream:
            for field_name, meta in self._betterproto.meta_by_field_name.items():
                value = getattr(self, field_name)

                if value is None:
                    # Optional items should be skipped. This is used for the Google
                    # wrapper types and proto3 field presence/optional fields.
                    continue

                if value == self._get_field_default(field_name):
                    # Default (zero) values are not serialized.
                    continue

                if isinstance(value, list):
                    if meta.proto_type in PACKED_TYPES:
                        # Packed lists look like a length-delimited field. First,
                        # preprocess/encode each value into a buffer and then
                        # treat it like a field of raw bytes.
                        buf = bytearray()
                        for item in value:
                            buf += _preprocess_single(meta.proto_type, None, item)
                        stream.write(_serialize_single(meta.number, TYPE_BYTES, buf))
                    else:
                        for item in value:
                            stream.write(
                                _serialize_single(
                                    meta.number,
                                    meta.proto_type,
                                    item,
                                    unwrap=meta.unwrap,
                                )
                                # if it's an empty message it still needs to be
                                # represented as an item in the repeated list
                                or b"\n\x00"
                            )

                elif isinstance(value, dict):
                    for k, v in value.items():
                        assert meta.map_meta
                        sk = _serialize_single(1, meta.map_meta[0].proto_type, k)
                        sv = _serialize_single(2, meta.map_meta[1].proto_type, v, unwrap=meta.map_meta[1].unwrap)
                        stream.write(_serialize_single(meta.number, meta.proto_type, sk + sv))
                else:
                    stream.write(
                        _serialize_single(
                            meta.number,
                            meta.proto_type,
                            value,
                            unwrap=meta.unwrap,
                        )
                    )

            stream.write(self._unknown_fields)
            return stream.getvalue()

    # For compatibility with other libraries
    def SerializeToString(self) -> bytes:
        """
        Get the binary encoded Protobuf representation of this message instance.

        .. note::
            This is a method for compatibility with other libraries,
            you should really use ``bytes(x)``.

        Returns
        --------
        :class:`bytes`
            The binary encoded Protobuf representation of this message instance
        """
        return bytes(self)

    def __reduce__(self) -> tuple[Any, ...]:
        # To support pickling
        return (self.__class__.parse, (bytes(self),))

    @classmethod
    def _type_hint(cls, field_name: str) -> type:
        return cls._type_hints()[field_name]

    @classmethod
    def _type_hints(cls) -> dict[str, type]:
        module = sys.modules[cls.__module__]
        return get_type_hints(cls, module.__dict__, {})

    @classmethod
    def _cls_for(cls, field: dataclasses.Field, index: int = 0) -> type:
        """Get the message class for a field from the type hints."""
        field_cls = cls._type_hint(field.name)
        if hasattr(field_cls, "__args__") and index >= 0 and field_cls.__args__ is not None:
            field_cls = field_cls.__args__[index]
        return field_cls

    def _get_field_default(self, field_name: str) -> Any:
        with warnings.catch_warnings():
            # ignore warnings when initialising deprecated field defaults
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            return self._betterproto.default_gen[field_name]()

    def _postprocess_single(self, wire_type: int, meta: FieldMetadata, field_name: str, value: Any) -> Any:
        """Adjusts values after parsing."""
        if wire_type == WIRE_VARINT:
            if meta.proto_type in (TYPE_INT32, TYPE_INT64):
                bits = 32 if meta.proto_type == TYPE_INT32 else 64
                value = value & ((1 << bits) - 1)
                signbit = 1 << (bits - 1)
                value = int((value ^ signbit) - signbit)
            elif meta.proto_type in (TYPE_UINT32, TYPE_UINT64):
                bits = 32 if meta.proto_type == TYPE_UINT32 else 64
                value = value & ((1 << bits) - 1)
            elif meta.proto_type in (TYPE_SINT32, TYPE_SINT64):
                bits = 32 if meta.proto_type == TYPE_SINT32 else 64
                value = value & ((1 << bits) - 1)
                value = (value >> 1) ^ (-(value & 1))  # Undo zig-zag encoding
            elif meta.proto_type == TYPE_BOOL:
                # Booleans use a varint encoding, so convert it to true/false.
                value = value > 0
            elif meta.proto_type == TYPE_ENUM:
                # Convert enum ints to python enum instances
                value = self._betterproto.cls_by_field[field_name](value)
        elif wire_type in (WIRE_FIXED_32, WIRE_FIXED_64):
            fmt = _pack_fmt(meta.proto_type)
            value = struct.unpack(fmt, value)[0]
        elif wire_type == WIRE_LEN_DELIM:
            if meta.proto_type == TYPE_STRING:
                value = str(value, "utf-8")
            elif meta.proto_type == TYPE_MESSAGE:
                if meta.unwrap:
                    msg_cls = meta.unwrap()
                else:
                    msg_cls = self._betterproto.cls_by_field[field_name]

                value = msg_cls.parse(value)

                if meta.unwrap:
                    value = value.to_wrapped()
            elif meta.proto_type == TYPE_MAP:
                value = self._betterproto.cls_by_field[field_name].parse(value)

        return value

    def load(
        self: T,
        stream: SupportsRead[bytes],
        size: int | None = None,
    ) -> T:
        """
        Load the binary encoded Protobuf from a stream into this message instance. This
        returns the instance itself and is therefore assignable and chainable.

        Parameters
        -----------
        stream: :class:`bytes`
            The stream to load the message from.
        size: :class:`Optional[int]`
            The size of the message in the stream.
            Reads stream until EOF if ``None`` is given.
            Reads based on a size delimiter prefix varint if SIZE_DELIMITED is given.

        Returns
        --------
        :class:`Message`
            The initialized message.
        """
        # If the message is delimited, parse the message delimiter
        if size == SIZE_DELIMITED:
            size, _ = load_varint(stream)

        # Got some data over the wire
        proto_meta = self._betterproto
        read = 0
        for parsed in load_fields(stream):
            field_name = proto_meta.field_name_by_number.get(parsed.number)
            if not field_name:
                self._unknown_fields += parsed.raw
                continue

            meta = proto_meta.meta_by_field_name[field_name]

            value: Any
            if parsed.wire_type == WIRE_LEN_DELIM and meta.proto_type in PACKED_TYPES:
                # This is a packed repeated field.
                pos = 0
                value = []
                while pos < len(parsed.value):
                    if meta.proto_type in (TYPE_FLOAT, TYPE_FIXED32, TYPE_SFIXED32):
                        decoded, pos = parsed.value[pos : pos + 4], pos + 4
                        wire_type = WIRE_FIXED_32
                    elif meta.proto_type in (TYPE_DOUBLE, TYPE_FIXED64, TYPE_SFIXED64):
                        decoded, pos = parsed.value[pos : pos + 8], pos + 8
                        wire_type = WIRE_FIXED_64
                    else:
                        decoded, pos = decode_varint(parsed.value, pos)
                        wire_type = WIRE_VARINT
                    decoded = self._postprocess_single(wire_type, meta, field_name, decoded)
                    value.append(decoded)
            else:
                value = self._postprocess_single(parsed.wire_type, meta, field_name, parsed.value)

            current = getattr(self, field_name)

            if meta.proto_type == TYPE_MAP:
                # Value represents a single key/value pair entry in the map.
                current[value.key] = value.value
            elif isinstance(current, list):
                if isinstance(value, list):
                    current.extend(value)
                else:
                    current.append(value)
            else:
                setattr(self, field_name, value)

            # If we have now loaded the expected length of the message, stop
            if size is not None:
                prev = read
                read += len(parsed.raw)
                if read == size:
                    break
                elif read > size:
                    raise ValueError(
                        f"Expected message of size {size}, can only read "
                        f"either {prev} or {read} bytes - there is no "
                        "message of the expected size in the stream."
                    )

        if size is not None and read < size:
            raise ValueError(
                f"Expected message of size {size}, but was only able to "
                f"read {read} bytes - the stream may have ended too soon,"
                " or the expected size may have been incorrect."
            )

        if self._is_pydantic():
            self._validate()

        return self

    @classmethod
    def parse(cls, data: bytes) -> Self:
        """
        Parse the binary encoded Protobuf into this message instance. This
        returns the instance itself and is therefore assignable and chainable.

        Parameters
        -----------
        data: :class:`bytes`
            The data to parse the message from.

        Returns
        --------
        :class:`Message`
            The initialized message.
        """
        with BytesIO(data) as stream:
            return cls().load(stream)

    # For compatibility with other libraries.
    @classmethod
    def FromString(cls: type[T], data: bytes) -> T:
        """
        Parse the binary encoded Protobuf into this message instance. This
        returns the instance itself and is therefore assignable and chainable.

        .. note::
            This is a method for compatibility with other libraries,
            you should really use :meth:`parse`.


        Parameters
        -----------
        data: :class:`bytes`
            The data to parse the protobuf from.

        Returns
        --------
        :class:`Message`
            The initialized message.
        """
        return cls.parse(data)

    def to_dict(
        self,
        *,
        output_format: OutputFormat = OutputFormat.PROTO_JSON,
        casing: Casing = Casing.CAMEL,
        include_default_values: bool = False,
    ) -> dict[str, Any]:
        """
        Return a dict representation of the message.

        Parameters
        -----------
        casing: :class:`Casing`
            The casing to use for key values. Default is :attr:`Casing.CAMEL` for
            compatibility purposes.
        include_default_values: :class:`bool`
            If ``True`` will include the default values of fields. Default is ``False``.
            E.g. an ``int32`` field will be included with a value of ``0`` if this is
            set to ``True``, otherwise this would be ignored.

        Returns
        --------
        Dict[:class:`str`, Any]
            The JSON serializable dict representation of this object.
        """
        if self._is_pydantic():
            self._validate()

        kwargs = {  # For recursive calls
            "output_format": output_format,
            "casing": casing,
            "include_default_values": include_default_values,
        }

        output: dict[str, Any] = {}
        field_types = self._type_hints()

        for field_name, meta in self._betterproto.meta_by_field_name.items():
            value = getattr(self, field_name)
            cased_name = casing(field_name).rstrip("_")  # type: ignore

            if meta.repeated or meta.optional:
                field_type = field_types[field_name].__args__[0]
            else:
                field_type = field_types[field_name]

            if meta.repeated:
                output_value = [_value_to_dict(v, meta.proto_type, field_type, meta.unwrap, **kwargs)[0] for v in value]
                if output_value or include_default_values:
                    output[cased_name] = output_value

            elif meta.proto_type == TYPE_MAP:
                assert meta.map_meta is not None
                field_type_k = field_types[field_name].__args__[0]
                field_type_v = field_types[field_name].__args__[1]
                output_map = {
                    _value_to_dict(k, meta.map_meta[0].proto_type, field_type_k, None, **kwargs)[0]: _value_to_dict(
                        v, meta.map_meta[1].proto_type, field_type_v, meta.map_meta[1].unwrap, **kwargs
                    )[0]
                    for k, v in value.items()
                }

                if output_map or include_default_values:
                    output[cased_name] = output_map

            else:
                if value is None:
                    output_value, is_default = None, True
                else:
                    output_value, is_default = _value_to_dict(value, meta.proto_type, field_type, meta.unwrap, **kwargs)
                    if meta.optional:
                        is_default = False

                if include_default_values or not is_default:
                    output[cased_name] = output_value

        return output

    @classmethod
    def _from_dict_init(cls, mapping: Mapping[str, Any] | Any, *, ignore_unknown_fields: bool) -> Mapping[str, Any]:
        init_kwargs: dict[str, Any] = {}
        for key, value in mapping.items():
            field_name = safe_snake_case(key)

            try:
                field_cls = cls._betterproto.cls_by_field[field_name]
                meta = cls._betterproto.meta_by_field_name[field_name]
            except KeyError:
                # According to the protobuf spec (https://protobuf.dev/programming-guides/json/): "The protobuf JSON
                # parser should reject unknown fields by default but may provide an option to ignore unknown fields in
                # parsing."
                if ignore_unknown_fields:
                    continue

                raise KeyError(f"Unknown field '{field_name}' in message {cls.__name__}.") from None

            if value is None:
                continue

            if meta.proto_type == TYPE_MESSAGE:
                if meta.repeated:
                    value = [_value_from_dict(item, meta, field_cls) for item in value]
                else:
                    value = _value_from_dict(value, meta, field_cls)

            elif meta.proto_type == TYPE_MAP:
                assert meta.map_meta
                assert isinstance(value, dict)

                value_cls = cls._betterproto.cls_by_field[f"{field_name}.value"]

                value = {
                    _value_from_dict(k, meta.map_meta[0], type(None)): _value_from_dict(v, meta.map_meta[1], value_cls)
                    for k, v in value.items()
                }

            elif meta.repeated:
                value = [_value_from_dict(item, meta, field_cls) for item in value]

            else:
                value = _value_from_dict(value, meta, field_cls)

            init_kwargs[field_name] = value
        return init_kwargs

    @classmethod
    def from_dict(cls: type[Self], value: Mapping[str, Any] | Any, *, ignore_unknown_fields: bool = False) -> Self:
        """
        Parse the key/value pairs into the a new message instance.

        Parameters
        -----------
        value: Dict[:class:`str`, Any]
            The dictionary to parse from.

        Returns
        --------
        :class:`Message`
            The initialized message.
        """
        if not isinstance(value, Mapping) and hasattr(cls, "from_wrapped"):  # type: ignore
            return cls.from_wrapped(value)  # type: ignore

        return cls(**cls._from_dict_init(value, ignore_unknown_fields=ignore_unknown_fields))  # type: ignore

    def to_json(
        self,
        indent: None | int | str = None,
        include_default_values: bool = False,
        casing: Casing = Casing.CAMEL,
    ) -> str:
        """A helper function to parse the message instance into its JSON
        representation.

        This is equivalent to::

            json.dumps(message.to_dict(), indent=indent)

        Parameters
        -----------
        indent: Optional[Union[:class:`int`, :class:`str`]]
            The indent to pass to :func:`json.dumps`.

        include_default_values: :class:`bool`
            If ``True`` will include the default values of fields. Default is ``False``.
            E.g. an ``int32`` field will be included with a value of ``0`` if this is
            set to ``True``, otherwise this would be ignored.

        casing: :class:`Casing`
            The casing to use for key values. Default is :attr:`Casing.CAMEL` for
            compatibility purposes.

        Returns
        --------
        :class:`str`
            The JSON representation of the message.
        """
        return json.dumps(
            self.to_dict(include_default_values=include_default_values, casing=casing),
            indent=indent,
        )

    @classmethod
    def from_json(cls, value: str | bytes, *, ignore_unknown_fields: bool = False) -> Self:
        """A helper function to return the message instance from its JSON
        representation. This returns the instance itself and is therefore assignable
        and chainable.

        This is equivalent to::

            return message.from_dict(json.loads(value))

        Parameters
        -----------
        value: Union[:class:`str`, :class:`bytes`]
            The value to pass to :func:`json.loads`.

        Returns
        --------
        :class:`Message`
            The initialized message.
        """
        return cls.from_dict(json.loads(value), ignore_unknown_fields=ignore_unknown_fields)

    def is_set(self, name: str) -> bool:
        """
        Check if field with the given name has been set.

        Parameters
        -----------
        name: :class:`str`
            The name of the field to check for.

        Returns
        --------
        :class:`bool`
            `True` if field has been set, otherwise `False`.
        """
        return self.__getattribute__(name) is not self._get_field_default(name)

    @classmethod
    def _validate_field_groups(cls, values):
        group_to_one_ofs = cls._betterproto.oneof_field_by_group
        field_name_to_meta = cls._betterproto.meta_by_field_name

        for group, field_set in group_to_one_ofs.items():
            if len(field_set) == 1:
                (field,) = field_set
                field_name = field.name
                meta = field_name_to_meta[field_name]

                # This is a synthetic oneof; we should ignore it's presence and not
                # consider it as a oneof.
                if meta.optional:
                    continue

            set_fields = [field.name for field in field_set if getattr(values, field.name, None) is not None]

            if len(set_fields) > 1:
                set_fields_str = ", ".join(set_fields)
                raise ValueError(f"Group {group} has more than one value; fields {set_fields_str} are not None")

        return values


Message.__annotations__ = {}  # HACK to avoid typing.get_type_hints breaking :)


# The Rust codec is not available for now
# try:
#     import betterproto2_rust_codec  # pyright: ignore[reportMissingImports]
# except ModuleNotFoundError:
#     pass
# else:

#     def parse_patched(self, data: bytes) -> Message:
#         betterproto2_rust_codec.deserialize(self, data)
#         return self

#     def bytes_patched(self) -> bytes:
#         return betterproto2_rust_codec.serialize(self)

#     Message.parse = parse_patched
#     Message.__bytes__ = bytes_patched


def which_one_of(message: Message, group_name: str) -> tuple[str, Any | None]:
    """
    Return the name and value of a message's one-of field group.

    Returns
    --------
    Tuple[:class:`str`, Any]
        The field name and the value for that field.
    """
    field_name, value = "", None
    for field in message._betterproto.oneof_field_by_group[group_name]:
        v = getattr(message, field.name)

        if v is not None:
            if field_name:
                raise RuntimeError(f"more than one field set in oneof: {field.name} and {field_name}")
            field_name, value = field.name, v

    return field_name, value
