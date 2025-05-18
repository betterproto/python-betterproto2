import pydantic
import pytest


def test_manual_validation():
    from tests.output_betterproto_pydantic.manual_validation import Msg

    msg = Msg()

    msg.x = 12
    msg._validate()

    msg.x = 2**50  # This is an invalid int32 value
    with pytest.raises(pydantic.ValidationError):
        msg._validate()


def test_manual_validation_non_pydantic():
    from tests.output_betterproto.manual_validation import Msg

    # Validation is not available for non-pydantic messages
    with pytest.raises(TypeError):
        Msg()._validate()
