import asyncio
import threading
from collections.abc import AsyncIterator

import grpc
import grpclib
import pytest
from grpclib.server import Server

from tests.output_betterproto.simple_service import (
    Request,
    Response,
    SimpleServiceBase,
    SimpleServiceSyncStub,
)


class SimpleService(SimpleServiceBase):
    async def get_unary_unary(self, message: "Request") -> "Response":
        return Response(message=f"Hello {message.value}")

    async def get_unary_stream(self, message: "Request") -> "AsyncIterator[Response]":
        async for _ in range(5):
            yield Response(message=f"Hello {message.value}")

    async def get_stream_unary(self, messages: "AsyncIterator[Request]") -> "Response":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_stream_stream(self, messages: "AsyncIterator[Request]") -> "AsyncIterator[Response]":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)


@pytest.mark.asyncio
async def test_sync_client():
    def start_server():
        async def run_server():
            server = Server([SimpleService()])
            await server.start("127.0.0.1", 1234)
            await asyncio.sleep(3)  # Close the server after 3 seconds
            server.close()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_server())
        loop.close()

    # We need to start the server in a new thread to avoid a deadlock
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Create a sync client
    with grpc.insecure_channel("localhost:1234") as channel:
        client = SimpleServiceSyncStub(channel)
        response = client.get_unary_unary(Request(value=42))
        assert response.message == "Hello 42"

    # Create an async client
    # client = SimpleServiceStub(Channel(host="127.0.0.1", port=1234))
    # response = await client.get_unary_unary(Request(value=42))
    # assert response.message == "Hello 42"
