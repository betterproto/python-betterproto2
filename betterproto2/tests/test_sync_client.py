import asyncio
import threading
from collections.abc import AsyncIterator

import grpc
import pytest
from grpclib.server import Server

from tests.output_betterproto.simple_service import Request, Response, SimpleServiceBase, SimpleServiceSyncStub


class SimpleService(SimpleServiceBase):
    async def get_unary_unary(self, message: "Request") -> "Response":
        return Response(message=f"Hello {message.value}")

    async def get_unary_stream(self, message: "Request") -> "AsyncIterator[Response]":
        for i in range(5):
            yield Response(message=f"Hello {message.value} {i}")

    async def get_stream_unary(self, messages: "AsyncIterator[Request]") -> "Response":
        s = 0
        async for m in messages:
            s += m.value
        return Response(message=f"Hello {s}")

    async def get_stream_stream(self, messages: "AsyncIterator[Request]") -> "AsyncIterator[Response]":
        async for message in messages:
            yield Response(message=f"Hello {message.value}")


@pytest.mark.asyncio
async def test_sync_client():
    start_server_event = threading.Event()
    close_server_event = asyncio.Event()

    def start_server():
        async def run_server():
            server = Server([SimpleService()])
            await server.start("127.0.0.1", 1234)
            start_server_event.set()

            await close_server_event.wait()
            server.close()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_server())
        loop.close()

    # We need to start the server in a new thread to avoid a deadlock
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Create a sync client
    start_server_event.wait()

    with grpc.insecure_channel("localhost:1234") as channel:
        client = SimpleServiceSyncStub(channel)

        response = client.get_unary_unary(Request(value=42))
        assert response.message == "Hello 42"

        response = client.get_unary_stream(Request(value=42))
        assert [r.message for r in response] == [f"Hello 42 {i}" for i in range(5)]

        response = client.get_stream_unary([Request(value=i) for i in range(5)])
        assert response.message == "Hello 10"

        response = client.get_stream_stream([Request(value=i) for i in range(5)])
        assert [r.message for r in response] == [f"Hello {i}" for i in range(5)]

        close_server_event.set()

    # Create an async client
    # client = SimpleServiceStub(Channel(host="127.0.0.1", port=1234))
    # response = await client.get_unary_unary(Request(value=42))
    # assert response.message == "Hello 42"
