import asyncio
from typing import Generic, TypeVar

import pytest
from google.protobuf import descriptor_pb2
from grpclib.reflection.service import ServerReflection
from grpclib.reflection.v1.reflection_grpc import ServerReflectionBase as ServerReflectionBaseV1
from grpclib.reflection.v1alpha.reflection_grpc import ServerReflectionBase as ServerReflectionBaseV1Alpha
from grpclib.testing import ChannelFor

from tests.output_betterproto.example_service import TestBase
from tests.output_betterproto.grpc.reflection.v1 import (
    ErrorResponse,
    ListServiceResponse,
    ServerReflectionRequest,
    ServerReflectionStub,
    ServiceResponse,
)
from tests.output_betterproto_descriptor.google_proto_descriptor_pool import default_google_proto_descriptor_pool


class TestService(TestBase):
    pass


T = TypeVar("T")


class AsyncIterableQueue(Generic[T]):
    CLOSED_SENTINEL = object()

    def __init__(self):
        self._queue = asyncio.Queue()
        self._done = asyncio.Event()

    def put(self, item: T):
        self._queue.put_nowait(item)

    def close(self):
        self._queue.put_nowait(self.CLOSED_SENTINEL)

    def __aiter__(self):
        return self

    async def __anext__(self) -> T:
        val = await self._queue.get()
        if val is self.CLOSED_SENTINEL:
            raise StopAsyncIteration
        return val


@pytest.mark.asyncio
async def test_grpclib_reflection():
    service = TestService()
    services = ServerReflection.extend([service])
    for service in services:
        # This won't be needed once https://github.com/vmagamedov/grpclib/pull/204 is in.
        if isinstance(service, ServerReflectionBaseV1Alpha | ServerReflectionBaseV1):
            service._pool = default_google_proto_descriptor_pool

    async with ChannelFor(services) as channel:
        requests = AsyncIterableQueue[ServerReflectionRequest]()
        responses = ServerReflectionStub(channel).server_reflection_info(requests)

        # list services
        requests.put(ServerReflectionRequest(list_services=""))
        response = await anext(responses)
        assert response.list_services_response == ListServiceResponse(
            service=[ServiceResponse(name="example_service.Test")]
        )

        # list methods

        # should fail before we've added descriptors to the protobuf pool
        requests.put(ServerReflectionRequest(file_containing_symbol="example_service.Test"))
        response = await anext(responses)
        assert response.error_response == ErrorResponse(error_code=5, error_message="not found")
        assert response.file_descriptor_response is None

        # now it should work
        import tests.output_betterproto_descriptor.example_service as example_service_with_desc

        requests.put(ServerReflectionRequest(file_containing_symbol="example_service.Test"))
        response = await anext(responses)
        expected = descriptor_pb2.FileDescriptorProto.FromString(
            example_service_with_desc.EXAMPLE_SERVICE_PROTO_DESCRIPTOR.serialized_pb
        )
        assert response.error_response is None
        assert response.file_descriptor_response is not None
        assert len(response.file_descriptor_response.file_descriptor_proto) == 1
        actual = descriptor_pb2.FileDescriptorProto.FromString(
            response.file_descriptor_response.file_descriptor_proto[0]
        )
        assert actual == expected

        requests.close()

        await anext(responses, None)
