import asyncio
import uuid
from typing import TYPE_CHECKING

import pytest

from tests.util import requires_grpclib  # noqa: F401

if TYPE_CHECKING:
    from tests.outputs.service.service import TestStub as ThingServiceClient


async def _test_client(client: "ThingServiceClient", name="clean room", **kwargs):
    from tests.outputs.service.service import DoThingRequest

    response = await client.do_thing(DoThingRequest(name=name), **kwargs)
    assert response.names == [name]


def _assert_request_meta_received(deadline, metadata):
    def server_side_test(stream):
        assert stream.deadline._timestamp == pytest.approx(deadline._timestamp, 1), (
            "The provided deadline should be received serverside"
        )
        assert stream.metadata["authorization"] == metadata["authorization"], (
            "The provided authorization metadata should be received serverside"
        )

    return server_side_test


@pytest.fixture
def handler_trailer_only_unauthenticated():
    import grpclib
    import grpclib.server

    async def handler(stream: grpclib.server.Stream):
        await stream.recv_message()
        await stream.send_initial_metadata()
        await stream.send_trailing_metadata(status=grpclib.Status.UNAUTHENTICATED)

    return handler


@pytest.mark.asyncio
async def test_simple_service_call(requires_grpclib):
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import TestStub as ThingServiceClient

    from .thing_service import ThingService

    async with ChannelFor([ThingService()]) as channel:
        await _test_client(ThingServiceClient(channel))


@pytest.mark.asyncio
async def test_trailer_only_error_unary_unary(mocker, requires_grpclib, handler_trailer_only_unauthenticated):
    import grpclib
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import DoThingRequest, TestStub as ThingServiceClient

    from .thing_service import ThingService

    service = ThingService()
    mocker.patch.object(
        service,
        "do_thing",
        side_effect=handler_trailer_only_unauthenticated,
        autospec=True,
    )
    async with ChannelFor([service]) as channel:
        with pytest.raises(grpclib.exceptions.GRPCError) as e:
            await ThingServiceClient(channel).do_thing(DoThingRequest(name="something"))
        assert e.value.status == grpclib.Status.UNAUTHENTICATED


@pytest.mark.asyncio
async def test_trailer_only_error_stream_unary(mocker, requires_grpclib, handler_trailer_only_unauthenticated):
    import grpclib
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import (
        DoThingRequest,
        TestStub as ThingServiceClient,
    )

    from .thing_service import ThingService

    service = ThingService()
    mocker.patch.object(
        service,
        "do_many_things",
        side_effect=handler_trailer_only_unauthenticated,
        autospec=True,
    )
    async with ChannelFor([service]) as channel:
        with pytest.raises(grpclib.exceptions.GRPCError) as e:
            await ThingServiceClient(channel).do_many_things(messages=[DoThingRequest(name="something")])
            await _test_client(ThingServiceClient(channel))
        assert e.value.status == grpclib.Status.UNAUTHENTICATED


@pytest.mark.asyncio
async def test_service_call_mutable_defaults(mocker, requires_grpclib):
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import TestStub as ThingServiceClient

    from .thing_service import ThingService

    async with ChannelFor([ThingService()]) as channel:
        client = ThingServiceClient(channel)
        spy = mocker.spy(client, "_unary_unary")
        await _test_client(client)
        comments = spy.call_args_list[-1].args[1].comments
        await _test_client(client)
        assert spy.call_args_list[-1].args[1].comments is not comments


@pytest.mark.asyncio
async def test_service_call_with_upfront_request_params(requires_grpclib):
    import grpclib
    import grpclib.metadata
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import TestStub as ThingServiceClient

    from .thing_service import ThingService

    # Setting deadline
    deadline = grpclib.metadata.Deadline.from_timeout(22)
    metadata = {"authorization": "12345"}
    async with ChannelFor([ThingService(test_hook=_assert_request_meta_received(deadline, metadata))]) as channel:
        await _test_client(ThingServiceClient(channel, deadline=deadline, metadata=metadata))

    # Setting timeout
    timeout = 99
    deadline = grpclib.metadata.Deadline.from_timeout(timeout)
    metadata = {"authorization": "12345"}
    async with ChannelFor([ThingService(test_hook=_assert_request_meta_received(deadline, metadata))]) as channel:
        await _test_client(ThingServiceClient(channel, timeout=timeout, metadata=metadata))


@pytest.mark.asyncio
async def test_service_call_lower_level_with_overrides(requires_grpclib):
    import grpclib
    import grpclib.metadata
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import (
        DoThingRequest,
        DoThingResponse,
        TestStub as ThingServiceClient,
    )

    from .thing_service import ThingService

    THING_TO_DO = "get milk"

    # Setting deadline
    deadline = grpclib.metadata.Deadline.from_timeout(22)
    metadata = {"authorization": "12345"}
    kwarg_deadline = grpclib.metadata.Deadline.from_timeout(28)
    kwarg_metadata = {"authorization": "12345"}
    async with ChannelFor([ThingService(test_hook=_assert_request_meta_received(deadline, metadata))]) as channel:
        client = ThingServiceClient(channel, deadline=deadline, metadata=metadata)
        response = await client._unary_unary(
            "/service.Test/DoThing",
            DoThingRequest(THING_TO_DO),
            DoThingResponse,
            deadline=kwarg_deadline,
            metadata=kwarg_metadata,
        )
        assert response.names == [THING_TO_DO]

    # Setting timeout
    timeout = 99
    deadline = grpclib.metadata.Deadline.from_timeout(timeout)
    metadata = {"authorization": "12345"}
    kwarg_timeout = 9000
    kwarg_deadline = grpclib.metadata.Deadline.from_timeout(kwarg_timeout)
    kwarg_metadata = {"authorization": "09876"}
    async with ChannelFor(
        [
            ThingService(
                test_hook=_assert_request_meta_received(kwarg_deadline, kwarg_metadata),
            )
        ]
    ) as channel:
        client = ThingServiceClient(channel, deadline=deadline, metadata=metadata)
        response = await client._unary_unary(
            "/service.Test/DoThing",
            DoThingRequest(THING_TO_DO),
            DoThingResponse,
            timeout=kwarg_timeout,
            metadata=kwarg_metadata,
        )
        assert response.names == [THING_TO_DO]


@pytest.mark.asyncio
async def test_service_call_high_level_with_overrides(mocker, requires_grpclib):
    import grpclib
    import grpclib.client
    import grpclib.metadata
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import TestStub as ThingServiceClient

    from .thing_service import ThingService

    overrides = [
        dict(timeout=10),
        dict(deadline=grpclib.metadata.Deadline.from_timeout(10)),
        dict(metadata={"authorization": str(uuid.uuid4())}),
        dict(timeout=20, metadata={"authorization": str(uuid.uuid4())}),
    ]

    for override in overrides:
        request_spy = mocker.spy(grpclib.client.Channel, "request")
        name = str(uuid.uuid4())
        defaults = dict(
            timeout=99,
            deadline=grpclib.metadata.Deadline.from_timeout(99),
            metadata={"authorization": name},
        )

        async with ChannelFor(
            [
                ThingService(
                    test_hook=_assert_request_meta_received(
                        deadline=grpclib.metadata.Deadline.from_timeout(override.get("timeout", 99)),
                        metadata=override.get("metadata", defaults.get("metadata")),
                    )
                )
            ]
        ) as channel:
            client = ThingServiceClient(channel, **defaults)
            await _test_client(client, name=name, **override)
            assert request_spy.call_count == 1

            request_spy_call_kwargs = request_spy.call_args.kwargs

            # ensure all overrides were successful
            for key, value in override.items():
                assert key in request_spy_call_kwargs
                assert request_spy_call_kwargs[key] == value

            # ensure default values were retained
            for key in set(defaults.keys()) - set(override.keys()):
                assert key in request_spy_call_kwargs
                assert request_spy_call_kwargs[key] == defaults[key]

        mocker.stop(request_spy)


@pytest.mark.asyncio
async def test_async_gen_for_unary_stream_request(requires_grpclib):
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import GetThingRequest, TestStub as ThingServiceClient

    from .thing_service import ThingService

    thing_name = "my milkshakes"

    async with ChannelFor([ThingService()]) as channel:
        client = ThingServiceClient(channel)
        expected_versions = [5, 4, 3, 2, 1]
        async for response in client.get_thing_versions(GetThingRequest(name=thing_name)):
            assert response.name == thing_name
            assert response.version == expected_versions.pop()


@pytest.mark.asyncio
async def test_async_gen_for_stream_stream_request(requires_grpclib):
    from grpclib.testing import ChannelFor

    from tests.grpc.async_channel import AsyncChannel
    from tests.outputs.service.service import GetThingRequest, TestStub as ThingServiceClient

    from .thing_service import ThingService

    some_things = ["cake", "cricket", "coral reef"]
    more_things = ["ball", "that", "56kmodem", "liberal humanism", "cheesesticks"]
    expected_things = (*some_things, *more_things)

    async with ChannelFor([ThingService()]) as channel:
        client = ThingServiceClient(channel)
        # Use an AsyncChannel to decouple sending and recieving, it'll send some_things
        # immediately and we'll use it to send more_things later, after recieving some
        # results
        request_chan = AsyncChannel()
        send_initial_requests = asyncio.ensure_future(
            request_chan.send_from(GetThingRequest(name) for name in some_things)
        )
        response_index = 0
        async for response in client.get_different_things(request_chan):
            assert response.name == expected_things[response_index]
            assert response.version == response_index + 1
            response_index += 1
            if more_things:
                # Send some more requests as we receive responses to be sure coordination of
                # send/receive events doesn't matter
                await request_chan.send(GetThingRequest(more_things.pop(0)))
            elif not send_initial_requests.done():
                # Make sure the sending task it completed
                await send_initial_requests
            else:
                # No more things to send make sure channel is closed
                request_chan.close()
        assert response_index == len(expected_things), "Didn't receive all expected responses"


@pytest.mark.asyncio
async def test_stream_unary_with_empty_iterable(requires_grpclib):
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import DoThingRequest, TestStub as ThingServiceClient

    from .thing_service import ThingService

    things = []  # empty

    async with ChannelFor([ThingService()]) as channel:
        client = ThingServiceClient(channel)
        requests = [DoThingRequest(name) for name in things]
        response = await client.do_many_things(requests)
        assert len(response.names) == 0


@pytest.mark.asyncio
async def test_stream_stream_with_empty_iterable(requires_grpclib):
    from grpclib.testing import ChannelFor

    from tests.outputs.service.service import GetThingRequest, TestStub as ThingServiceClient

    from .thing_service import ThingService

    things = []  # empty

    async with ChannelFor([ThingService()]) as channel:
        client = ThingServiceClient(channel)
        requests = [GetThingRequest(name) for name in things]
        responses = [response async for response in client.get_different_things(requests)]
        assert len(responses) == 0
