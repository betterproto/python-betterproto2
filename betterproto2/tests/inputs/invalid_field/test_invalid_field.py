import pytest

from tests.util import requires_pydantic  # noqa: F401


def test_invalid_field():
    from tests.outputs.invalid_field.invalid_field import Test

    with pytest.raises(TypeError):
        Test(unknown_field=12)


def test_invalid_field_pydantic(requires_pydantic):
    from pydantic import ValidationError

    from tests.outputs.invalid_field_pydantic.invalid_field import Test

    with pytest.raises(ValidationError):
        Test(unknown_field=12)
