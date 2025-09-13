import betterproto2
from tests.util import get_test_case_json_data, requires_pydantic  # noqa: F401


def test_which_count():
    from tests.outputs.oneof.oneof import Test

    message = Test.from_json(get_test_case_json_data("oneof")[0].json)
    assert betterproto2.which_one_of(message, "foo") == ("pitied", 100)


def test_which_name():
    from tests.outputs.oneof.oneof import Test

    message = Test.from_json(get_test_case_json_data("oneof", "oneof_name.json")[0].json)
    assert betterproto2.which_one_of(message, "foo") == ("pitier", "Mr. T")


def test_which_count_pyd(requires_pydantic):
    from tests.outputs.oneof_pydantic.oneof import Test

    message = Test(pitier="Mr. T", just_a_regular_field=2, bar_name="a_bar")
    assert betterproto2.which_one_of(message, "foo") == ("pitier", "Mr. T")


def test_oneof_constructor_assign():
    from tests.outputs.oneof.oneof import MixedDrink, Test

    message = Test(mixed_drink=MixedDrink(shots=42))
    field, value = betterproto2.which_one_of(message, "bar")
    assert field == "mixed_drink"
    assert value.shots == 42
