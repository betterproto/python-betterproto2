import pytest

from tests.util import requires_pydantic  # noqa: F401


def test_value():
    from tests.outputs.bool.bool import Test

    message = Test()
    assert not message.value, "Boolean is False by default"


def test_pydantic_no_value(requires_pydantic):
    from tests.outputs.bool_pydantic.bool import Test as TestPyd

    message = TestPyd()
    assert not message.value, "Boolean is False by default"


def test_pydantic_value(requires_pydantic):
    from tests.outputs.bool_pydantic.bool import Test as TestPyd

    message = TestPyd(value=False)
    assert not message.value


def test_pydantic_bad_value(requires_pydantic):
    from tests.outputs.bool_pydantic.bool import Test as TestPyd

    with pytest.raises(ValueError):
        TestPyd(value=123)
