import pytest

from tests.util import requires_grpclib  # noqa: F401


@pytest.mark.asyncio
async def test_service_correctly_imports_reference_message(requires_grpclib):
    from tests.mocks import MockChannel
    from tests.outputs.import_service_input_message.import_service_input_message import (
        RequestMessage,
        RequestResponse,
        TestStub,
    )

    mock_response = RequestResponse(value=10)
    service = TestStub(MockChannel([mock_response]))
    response = await service.do_thing(RequestMessage(1))
    assert mock_response == response


@pytest.mark.asyncio
async def test_service_correctly_imports_reference_message_from_child_package(requires_grpclib):
    from tests.mocks import MockChannel
    from tests.outputs.import_service_input_message.import_service_input_message import (
        RequestResponse,
        TestStub,
    )
    from tests.outputs.import_service_input_message.import_service_input_message.child import (
        ChildRequestMessage,
    )

    mock_response = RequestResponse(value=10)
    service = TestStub(MockChannel([mock_response]))
    response = await service.do_thing_2(ChildRequestMessage(1))
    assert mock_response == response


@pytest.mark.asyncio
async def test_service_correctly_imports_nested_reference(requires_grpclib):
    from tests.mocks import MockChannel
    from tests.outputs.import_service_input_message.import_service_input_message import (
        NestedRequestMessage,
        RequestResponse,
        TestStub,
    )

    mock_response = RequestResponse(value=10)
    service = TestStub(MockChannel([mock_response]))
    response = await service.do_thing_3(NestedRequestMessage(1))
    assert mock_response == response
