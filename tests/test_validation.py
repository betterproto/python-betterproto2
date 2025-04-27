import pydantic
import pytest


def test_validation():
    from .output_betterproto_pydantic.validation import Message

    # Test int32 validation
    Message(int32_value=1)
    Message(int32_value=-(2**31))
    Message(int32_value=(2**31 - 1))
    with pytest.raises(pydantic.ValidationError):
        Message(int32_value=2**31)
    with pytest.raises(pydantic.ValidationError):
        Message(int32_value=-(2**31) - 1)

    # Test int64 validation
    Message(int64_value=1)
    Message(int64_value=-(2**63))
    Message(int64_value=(2**63 - 1))
    with pytest.raises(pydantic.ValidationError):
        Message(int64_value=2**63)
    with pytest.raises(pydantic.ValidationError):
        Message(int64_value=-(2**63) - 1)

    # Test uint32 validation
    Message(uint32_value=0)
    Message(uint32_value=2**32 - 1)
    with pytest.raises(pydantic.ValidationError):
        Message(uint32_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(uint32_value=2**32)

    # Test uint64 validation
    Message(uint64_value=0)
    Message(uint64_value=2**64 - 1)
    with pytest.raises(pydantic.ValidationError):
        Message(uint64_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(uint64_value=2**64)

    # Test sint32 validation
    Message(sint32_value=1)
    Message(sint32_value=-(2**31))
    Message(sint32_value=(2**31 - 1))
    with pytest.raises(pydantic.ValidationError):
        Message(sint32_value=2**31)
    with pytest.raises(pydantic.ValidationError):
        Message(sint32_value=-(2**31) - 1)

    # Test sint64 validation
    Message(sint64_value=1)
    Message(sint64_value=-(2**63))
    Message(sint64_value=(2**63 - 1))
    with pytest.raises(pydantic.ValidationError):
        Message(sint64_value=2**63)
    with pytest.raises(pydantic.ValidationError):
        Message(sint64_value=-(2**63) - 1)

    # Test fixed32 validation
    Message(fixed32_value=0)
    Message(fixed32_value=2**32 - 1)
    with pytest.raises(pydantic.ValidationError):
        Message(fixed32_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(fixed32_value=2**32)

    # Test fixed64 validation
    Message(fixed64_value=0)
    Message(fixed64_value=2**64 - 1)
    with pytest.raises(pydantic.ValidationError):
        Message(fixed64_value=-1)
    with pytest.raises(pydantic.ValidationError):
        Message(fixed64_value=2**64)

    # Test sfixed32 validation
    Message(sfixed32_value=1)
    Message(sfixed32_value=-(2**31))
    Message(sfixed32_value=(2**31 - 1))
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed32_value=2**31)
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed32_value=-(2**31) - 1)

    # Test sfixed64 validation
    Message(sfixed64_value=1)
    Message(sfixed64_value=-(2**63))
    Message(sfixed64_value=(2**63 - 1))
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed64_value=2**63)
    with pytest.raises(pydantic.ValidationError):
        Message(sfixed64_value=-(2**63) - 1)

    # Test float validation
    Message(float_value=0.0)
    Message(float_value=3.14)
    with pytest.raises(pydantic.ValidationError):
        Message(float_value=3.5e38)

    # Test string validation
    Message(string_value="")
    Message(string_value="Hello World")

    with pytest.raises(pydantic.ValidationError):
        Message(string_value="Hello \udc00 World")
