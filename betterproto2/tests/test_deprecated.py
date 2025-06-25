import warnings

import pytest

from tests.mocks import MockChannel
from tests.output_betterproto.deprecated import (
    Empty,
    Message,
    Test,
    TestNested,
    TestServiceStub,
)


@pytest.fixture
def message():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return Message(value="hello")


def test_deprecated_message():
    with pytest.warns(DeprecationWarning) as record:
        Message(value="hello")

    assert len(record) == 1
    assert str(record[0].message) == f"{Message.__name__} is deprecated"


def test_deprecated_nested_message_field():
    with pytest.warns(DeprecationWarning) as record:
        TestNested(nested_value="hello")

    assert len(record) == 1
    assert str(record[0].message) == f"TestNested.nested_value is deprecated"


def test_message_with_deprecated_field(message):
    with pytest.warns(DeprecationWarning) as record:
        Test(message=message, value=10)

    assert len(record) == 1
    assert str(record[0].message) == f"{Test.__name__}.message is deprecated"


def test_message_with_deprecated_field_not_set(message):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        Test(value=10)


def test_message_with_deprecated_field_not_set_default(message):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _ = Test(value=10).message


@pytest.mark.asyncio
async def test_service_with_deprecated_method():
    stub = TestServiceStub(MockChannel([Empty(), Empty()]))

    with pytest.warns(DeprecationWarning) as record:
        await stub.deprecated_func(Empty())

    assert len(record) == 1
    assert str(record[0].message) == f"TestService.deprecated_func is deprecated"

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        await stub.func(Empty())
