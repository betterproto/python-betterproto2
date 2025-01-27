import asyncio
from collections.abc import AsyncIterator

import pytest

from tests.grpc.async_channel import AsyncChannel
from tests.output_betterproto.stream_stream import Message


@pytest.fixture
def expected_responses():
    return [Message("Hello world 1"), Message("Hello world 2"), Message("Done")]


class ClientStub:
    async def connect(self, requests: AsyncIterator):
        await asyncio.sleep(0.1)
        async for request in requests:
            await asyncio.sleep(0.1)
            yield request
        await asyncio.sleep(0.1)
        yield Message("Done")


async def to_list(generator: AsyncIterator):
    return [value async for value in generator]


@pytest.fixture
def client():
    # channel = Channel(host='127.0.0.1', port=50051)
    # return ClientStub(channel)
    return ClientStub()


@pytest.mark.asyncio
async def test_send_from_before_connect_and_close_automatically(client, expected_responses):
    requests = AsyncChannel()
    await requests.send_from([Message(body="Hello world 1"), Message(body="Hello world 2")], close=True)
    responses = client.connect(requests)

    assert await to_list(responses) == expected_responses


@pytest.mark.asyncio
async def test_send_from_after_connect_and_close_automatically(client, expected_responses):
    requests = AsyncChannel()
    responses = client.connect(requests)
    await requests.send_from([Message(body="Hello world 1"), Message(body="Hello world 2")], close=True)

    assert await to_list(responses) == expected_responses


@pytest.mark.asyncio
async def test_send_from_close_manually_immediately(client, expected_responses):
    requests = AsyncChannel()
    responses = client.connect(requests)
    await requests.send_from([Message(body="Hello world 1"), Message(body="Hello world 2")], close=False)
    requests.close()

    assert await to_list(responses) == expected_responses


@pytest.mark.asyncio
async def test_send_individually_and_close_before_connect(client, expected_responses):
    requests = AsyncChannel()
    await requests.send(Message(body="Hello world 1"))
    await requests.send(Message(body="Hello world 2"))
    requests.close()
    responses = client.connect(requests)

    assert await to_list(responses) == expected_responses


@pytest.mark.asyncio
async def test_send_individually_and_close_after_connect(client, expected_responses):
    requests = AsyncChannel()
    await requests.send(Message(body="Hello world 1"))
    await requests.send(Message(body="Hello world 2"))
    responses = client.connect(requests)
    requests.close()

    assert await to_list(responses) == expected_responses
