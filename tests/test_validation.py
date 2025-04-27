import pydantic
import pytest


def test_int32_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(int32_value=1)
    Message(int32_value=-(2**31))
    Message(int32_value=(2**31 - 1))

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(int32_value=2**31)
    with pytest.raises(pydantic.ValidationError):
        Message(int32_value=-(2**31) - 1)


def test_int64_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(int64_value=1)
    Message(int64_value=-(2**63))
    Message(int64_value=(2**63 - 1))

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(int64_value=2**63)
    with pytest.raises(pydantic.ValidationError):
        Message(int64_value=-(2**63) - 1)


def test_uint32_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(uint32_value=0)
    Message(uint32_value=2**32 - 1)

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(uint32_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(uint32_value=2**32)


def test_uint64_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(uint64_value=0)
    Message(uint64_value=2**64 - 1)

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(uint64_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(uint64_value=2**64)


def test_sint32_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(sint32_value=1)
    Message(sint32_value=-(2**31))
    Message(sint32_value=(2**31 - 1))

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(sint32_value=2**31)
    with pytest.raises(pydantic.ValidationError):
        Message(sint32_value=-(2**31) - 1)


def test_sint64_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(sint64_value=1)
    Message(sint64_value=-(2**63))
    Message(sint64_value=(2**63 - 1))

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(sint64_value=2**63)
    with pytest.raises(pydantic.ValidationError):
        Message(sint64_value=-(2**63) - 1)


def test_fixed32_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(fixed32_value=0)
    Message(fixed32_value=2**32 - 1)

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(fixed32_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(fixed32_value=2**32)


def test_fixed64_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(fixed64_value=0)
    Message(fixed64_value=2**64 - 1)

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(fixed64_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(fixed64_value=2**64)


def test_sfixed32_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(sfixed32_value=1)
    Message(sfixed32_value=-(2**31))
    Message(sfixed32_value=(2**31 - 1))

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed32_value=2**31)
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed32_value=-(2**31) - 1)


def test_sfixed64_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(sfixed64_value=1)
    Message(sfixed64_value=-(2**63))
    Message(sfixed64_value=(2**63 - 1))

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed64_value=2**63)
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed64_value=-(2**63) - 1)


def test_float_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(float_value=0.0)
    Message(float_value=3.14)

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(float_value=3.5e38)


def test_string_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test valid values
    Message(string_value="")
    Message(string_value="Hello World")

    # Test invalid values
    with pytest.raises(pydantic.ValidationError):
        Message(string_value="Hello \udc00 World")
