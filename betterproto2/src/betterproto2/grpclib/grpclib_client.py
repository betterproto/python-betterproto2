import asyncio
from abc import ABC
from collections.abc import AsyncIterable, AsyncIterator, Collection, Iterable, Mapping
from typing import TYPE_CHECKING, Optional

import grpclib.const

if TYPE_CHECKING:
    from grpclib.client import Channel
    from grpclib.metadata import Deadline

    from .._types import IProtoMessage, T  # type: ignore[reportPrivateImportUsage]


Value = str | bytes
MetadataLike = Mapping[str, Value] | Collection[tuple[str, Value]]
MessageSource = Iterable["IProtoMessage"] | AsyncIterable["IProtoMessage"]


class ServiceStub(ABC):
    """
    Base class for async gRPC clients.
    """

    def __init__(
        self,
        channel: "Channel",
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: MetadataLike | None = None,
    ) -> None:
        self.channel = channel
        self.timeout = timeout
        self.deadline = deadline
        self.metadata = metadata

    def __resolve_request_kwargs(
        self,
        timeout: float | None,
        deadline: Optional["Deadline"],
        metadata: MetadataLike | None,
    ):
        return {
            "timeout": self.timeout if timeout is None else timeout,
            "deadline": self.deadline if deadline is None else deadline,
            "metadata": self.metadata if metadata is None else metadata,
        }

    async def _unary_unary(
        self,
        route: str,
        request: "IProtoMessage",
        response_type: type["T"],
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: MetadataLike | None = None,
    ) -> "T":
        """Make a unary request and return the response."""
        async with self.channel.request(
            route,
            grpclib.const.Cardinality.UNARY_UNARY,
            type(request),
            response_type,
            **self.__resolve_request_kwargs(timeout, deadline, metadata),
        ) as stream:
            await stream.send_message(request, end=True)
            response = await stream.recv_message()
        assert response is not None
        return response

    async def _unary_stream(
        self,
        route: str,
        request: "IProtoMessage",
        response_type: type["T"],
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: MetadataLike | None = None,
    ) -> AsyncIterator["T"]:
        """Make a unary request and return the stream response iterator."""
        async with self.channel.request(
            route,
            grpclib.const.Cardinality.UNARY_STREAM,
            type(request),
            response_type,
            **self.__resolve_request_kwargs(timeout, deadline, metadata),
        ) as stream:
            await stream.send_message(request, end=True)
            async for message in stream:
                yield message

    async def _stream_unary(
        self,
        route: str,
        request_iterator: MessageSource,
        request_type: type["IProtoMessage"],
        response_type: type["T"],
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: MetadataLike | None = None,
    ) -> "T":
        """Make a stream request and return the response."""
        async with self.channel.request(
            route,
            grpclib.const.Cardinality.STREAM_UNARY,
            request_type,
            response_type,
            **self.__resolve_request_kwargs(timeout, deadline, metadata),
        ) as stream:
            await stream.send_request()
            await self._send_messages(stream, request_iterator)
            response = await stream.recv_message()
        assert response is not None
        return response

    async def _stream_stream(
        self,
        route: str,
        request_iterator: MessageSource,
        request_type: type["IProtoMessage"],
        response_type: type["T"],
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: MetadataLike | None = None,
    ) -> AsyncIterator["T"]:
        """
        Make a stream request and return an AsyncIterator to iterate over response
        messages.
        """
        async with self.channel.request(
            route,
            grpclib.const.Cardinality.STREAM_STREAM,
            request_type,
            response_type,
            **self.__resolve_request_kwargs(timeout, deadline, metadata),
        ) as stream:
            await stream.send_request()
            sending_task = asyncio.ensure_future(self._send_messages(stream, request_iterator))
            try:
                async for response in stream:
                    yield response
            except:
                sending_task.cancel()
                raise

    @staticmethod
    async def _send_messages(stream, messages: MessageSource):
        if isinstance(messages, AsyncIterable):
            async for message in messages:
                await stream.send_message(message)
        else:
            for message in messages:
                await stream.send_message(message)
        await stream.end()
