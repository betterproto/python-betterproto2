from collections.abc import Callable

from .any import Any
from .duration import Duration
from .google_values import (
    BoolValue,
    BytesValue,
    DoubleValue,
    FloatValue,
    Int32Value,
    Int64Value,
    StringValue,
    UInt32Value,
    UInt64Value,
)
from .struct import ListValue, Struct, Value
from .timestamp import Timestamp

# For each (package, message name), lists the methods that should be added to the message definition.
# The source code of the method is read from the `known_types` folder. If imports are needed, they can be directly added
# to the template file: they will automatically be removed if not necessary.
KNOWN_METHODS: dict[tuple[str, str], list[Callable]] = {
    ("google.protobuf", "Any"): [Any.pack, Any.unpack, Any.to_dict, Any.from_dict],
    ("google.protobuf", "Timestamp"): [
        Timestamp.from_datetime,
        Timestamp.to_datetime,
        Timestamp.timestamp_to_json,
        Timestamp.from_dict,
        Timestamp.to_dict,
        Timestamp.from_wrapped,
        Timestamp.to_wrapped,
    ],
    ("google.protobuf", "Duration"): [
        Duration.from_timedelta,
        Duration.to_timedelta,
        Duration.delta_to_json,
        Duration.from_dict,
        Duration.to_dict,
        Duration.from_wrapped,
        Duration.to_wrapped,
    ],
    ("google.protobuf", "BoolValue"): [
        BoolValue.from_dict,
        BoolValue.to_dict,
        BoolValue.from_wrapped,
        BoolValue.to_wrapped,
    ],
    ("google.protobuf", "Int32Value"): [
        Int32Value.from_dict,
        Int32Value.to_dict,
        Int32Value.from_wrapped,
        Int32Value.to_wrapped,
    ],
    ("google.protobuf", "Int64Value"): [
        Int64Value.from_dict,
        Int64Value.to_dict,
        Int64Value.from_wrapped,
        Int64Value.to_wrapped,
    ],
    ("google.protobuf", "UInt32Value"): [
        UInt32Value.from_dict,
        UInt32Value.to_dict,
        UInt32Value.from_wrapped,
        UInt32Value.to_wrapped,
    ],
    ("google.protobuf", "UInt64Value"): [
        UInt64Value.from_dict,
        UInt64Value.to_dict,
        UInt64Value.from_wrapped,
        UInt64Value.to_wrapped,
    ],
    ("google.protobuf", "FloatValue"): [
        FloatValue.from_dict,
        FloatValue.to_dict,
        FloatValue.from_wrapped,
        FloatValue.to_wrapped,
    ],
    ("google.protobuf", "DoubleValue"): [
        DoubleValue.from_dict,
        DoubleValue.to_dict,
        DoubleValue.from_wrapped,
        DoubleValue.to_wrapped,
    ],
    ("google.protobuf", "StringValue"): [
        StringValue.from_dict,
        StringValue.to_dict,
        StringValue.from_wrapped,
        StringValue.to_wrapped,
    ],
    ("google.protobuf", "BytesValue"): [
        BytesValue.from_dict,
        BytesValue.to_dict,
        BytesValue.from_wrapped,
        BytesValue.to_wrapped,
    ],
    ("google.protobuf", "Struct"): [
        Struct.from_dict,
        Struct.to_dict,
        Struct.from_wrapped,
        Struct.to_wrapped,
    ],
    ("google.protobuf", "ListValue"): [
        ListValue.from_dict,
        ListValue.to_dict,
        ListValue.from_wrapped,
        ListValue.to_wrapped,
    ],
    ("google.protobuf", "Value"): [
        Value.from_dict,
        Value.to_dict,
        Value.from_wrapped,
        Value.to_wrapped,
    ],
}

# A wrapped type is the type of a message that is automatically replaced by a known Python type.
WRAPPED_TYPES: dict[tuple[str, str], str] = {
    ("google.protobuf", "BoolValue"): "bool",
    ("google.protobuf", "Int32Value"): "int",
    ("google.protobuf", "Int64Value"): "int",
    ("google.protobuf", "UInt32Value"): "int",
    ("google.protobuf", "UInt64Value"): "int",
    ("google.protobuf", "FloatValue"): "float",
    ("google.protobuf", "DoubleValue"): "float",
    ("google.protobuf", "StringValue"): "str",
    ("google.protobuf", "BytesValue"): "bytes",
    ("google.protobuf", "Timestamp"): "datetime.datetime",
    ("google.protobuf", "Duration"): "datetime.timedelta",
    ("google.protobuf", "Struct"): "dict[str, betterproto2.JSON]",
    ("google.protobuf", "ListValue"): "list[betterproto2.JSON]",
    ("google.protobuf", "Value"): "betterproto2.JSON",
}
