import math
import struct

import pytest

from betterproto2.validators.proto_types import (
    validate_float,
    validate_int32,
    validate_int64,
    validate_string,
    validate_uint32,
    validate_uint64,
)


def test_validate_int32():
    """Test that int32 validation works correctly for both valid and invalid cases."""
    # Valid values
    assert validate_int32(0) == 0
    assert validate_int32(1) == 1
    assert validate_int32(-1) == -1
    assert validate_int32(2**31 - 1) == 2**31 - 1
    assert validate_int32(-(2**31)) == -(2**31)

    # Invalid values
    with pytest.raises(ValueError, match="Value out of range for int32"):
        validate_int32(2**31)

    with pytest.raises(ValueError, match="Value out of range for int32"):
        validate_int32(-(2**31) - 1)


def test_validate_uint32():
    """Test that uint32 validation works correctly for both valid and invalid cases."""
    # Valid values
    assert validate_uint32(0) == 0
    assert validate_uint32(1) == 1
    assert validate_uint32(2**32 - 1) == 2**32 - 1

    # Invalid values
    with pytest.raises(ValueError, match="Value out of range for uint32"):
        validate_uint32(-1)

    with pytest.raises(ValueError, match="Value out of range for uint32"):
        validate_uint32(2**32)


def test_validate_int64():
    """Test that int64 validation works correctly for both valid and invalid cases."""
    # Valid values
    assert validate_int64(0) == 0
    assert validate_int64(1) == 1
    assert validate_int64(-1) == -1
    assert validate_int64(2**63 - 1) == 2**63 - 1
    assert validate_int64(-(2**63)) == -(2**63)

    # Invalid values
    with pytest.raises(ValueError, match="Value out of range for int64"):
        validate_int64(2**63)

    with pytest.raises(ValueError, match="Value out of range for int64"):
        validate_int64(-(2**63) - 1)


def test_validate_uint64():
    """Test that uint64 validation works correctly for both valid and invalid cases."""
    # Valid values
    assert validate_uint64(0) == 0
    assert validate_uint64(1) == 1
    assert validate_uint64(2**64 - 1) == 2**64 - 1

    # Invalid values
    with pytest.raises(ValueError, match="Value out of range for uint64"):
        validate_uint64(-1)

    with pytest.raises(ValueError, match="Value out of range for uint64"):
        validate_uint64(2**64)


def test_validate_float():
    """Test that float validation works correctly for both valid and invalid cases."""
    # Valid values
    assert validate_float(0.0) == 0.0
    assert validate_float(1.0) == 1.0
    assert validate_float(-1.0) == -1.0
    assert validate_float(3.14159) == 3.14159
    assert validate_float(1e-30) == 1e-30

    # Test the largest and smallest normal float32 values
    max_float32 = struct.unpack("!f", struct.pack("!f", 3.4028235e38))[0]
    min_float32 = struct.unpack("!f", struct.pack("!f", -3.4028235e38))[0]
    assert validate_float(max_float32) == max_float32
    assert validate_float(min_float32) == min_float32

    # Special values
    assert math.isnan(validate_float(float("nan")))
    assert validate_float(float("inf")) == float("inf")
    assert validate_float(float("-inf")) == float("-inf")

    # Invalid values
    with pytest.raises(ValueError, match="Value cannot be encoded as a float"):
        validate_float(3.5e38)  # Just over the max float32 value

    with pytest.raises(ValueError, match="Value cannot be encoded as a float"):
        validate_float(-3.5e38)  # Just under the min float32 value


def test_validate_string():
    """Test that string validation works correctly for both valid and invalid cases."""
    # Valid values
    assert validate_string("") == ""
    assert validate_string("hello") == "hello"
    assert validate_string("Hello, 世界!") == "Hello, 世界!"
    assert validate_string("π ≈ 3.14159") == "π ≈ 3.14159"

    # Invalid UTF-8
    with pytest.raises(ValueError, match="String contains invalid UTF-8 characters"):
        validate_string("\ud800")
