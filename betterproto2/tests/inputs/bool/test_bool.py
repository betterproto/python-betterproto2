import pytest


def test_value():
    from tests.output_betterproto.bool import Test

    message = Test()
    assert not message.value, "Boolean is False by default"


def test_pydantic_no_value():
    from tests.output_betterproto_pydantic.bool import Test as TestPyd

    message = TestPyd()
    assert not message.value, "Boolean is False by default"


def test_pydantic_value():
    from tests.output_betterproto_pydantic.bool import Test as TestPyd

    message = TestPyd(value=False)
    assert not message.value


def test_pydantic_bad_value():
    from tests.output_betterproto_pydantic.bool import Test as TestPyd

    with pytest.raises(ValueError):
        TestPyd(value=123)
