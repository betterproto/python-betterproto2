"""
Pydantic validators for Protocol Buffer standard types.

This module provides validator functions that can be used with Pydantic
to validate Protocol Buffer standard types (int32, int64, sfixed32, etc.)
to ensure they conform to their respective constraints.

These validators are designed to be used as "after validators", meaning the value
will already be of the correct type and only bounds checking is needed.
"""

import struct


def validate_float32(v: float) -> float:
    try:
        packed = struct.pack("!f", v)
        struct.unpack("!f", packed)
    except (struct.error, OverflowError):
        raise ValueError(f"Value cannot be encoded as a float: {v}")

    return v


def validate_string(v: str) -> str:
    try:
        v.encode("utf-8").decode("utf-8")
    except UnicodeError:
        raise ValueError("String contains invalid UTF-8 characters")
    return v
