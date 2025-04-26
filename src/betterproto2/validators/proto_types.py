"""
Pydantic validators for Protocol Buffer standard types.

This module provides validator functions that can be used with Pydantic
to validate Protocol Buffer standard types (int32, int64, sfixed32, etc.)
to ensure they conform to their respective constraints.

These validators are designed to be used as "after validators", meaning the value
will already be of the correct type and only bounds checking is needed.
"""

import struct


def validate_int32(v: int) -> int:
    if v < -(2**31) or v > 2**31 - 1:
        raise ValueError(f"Value out of range for int32: {v}")
    return v


def validate_uint32(v: int) -> int:
    if v < 0 or v > 2**32 - 1:
        raise ValueError(f"Value out of range for uint32: {v}")
    return v


def validate_int64(v: int) -> int:
    if v < -(2**63) or v > 2**63 - 1:
        raise ValueError(f"Value out of range for int64: {v}")
    return v


def validate_uint64(v: int) -> int:
    if v < 0 or v > 2**64 - 1:
        raise ValueError(f"Value out of range for uint64: {v}")
    return v


def validate_float(v: float) -> float:
    try:
        packed = struct.pack("!f", v)
        struct.unpack("!f", packed)[0]
    except (struct.error, OverflowError):
        raise ValueError(f"Value cannot be encoded as a float: {v}")

    return v


def validate_string(v: str) -> str:
    try:
        v.encode("utf-8").decode("utf-8")
    except UnicodeError:
        raise ValueError("String contains invalid UTF-8 characters")
    return v
