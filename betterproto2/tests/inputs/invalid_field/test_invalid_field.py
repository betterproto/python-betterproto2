import pytest


def test_invalid_field():
    from tests.outputs.invalid_field.invalid_field import Test

    with pytest.raises(TypeError):
        Test(unknown_field=12)


def test_invalid_field_pydantic():
    from pydantic import ValidationError

    from tests.outputs.invalid_field_pydantic.invalid_field import Test

    with pytest.raises(ValidationError):
        Test(unknown_field=12)
