"""Regression tests for ServiceStub attribute handling.

A generated RPC method is a class-level method on the ``ServiceStub`` subclass.
If its snake_cased name happens to collide with one of the base constructor
parameters (``channel``/``timeout``/``deadline``/``metadata`` — e.g. an RPC
literally named ``Metadata``), storing those parameters as plain instance
attributes would shadow the generated method, because an instance attribute
takes precedence over a class method during attribute lookup. The base class
keeps them under private names and exposes read-only properties instead, so a
subclass method overrides the property in the MRO. See issue #224.
"""

import pytest

from tests.mocks import MockChannel
from tests.util import requires_grpclib  # noqa: F401


@pytest.mark.asyncio
async def test_rpc_method_not_shadowed_by_constructor_param(requires_grpclib):
    from betterproto2.grpclib import ServiceStub

    class _StubWithCollidingRpc(ServiceStub):
        # Mimics a generated RPC named ``Metadata`` (snake_case ``metadata``),
        # which collides with the ``metadata`` constructor parameter.
        async def metadata(self):
            return "rpc-result"

    stub = _StubWithCollidingRpc(MockChannel(), metadata={"authorization": "token"})

    assert callable(stub.metadata), "RPC method must not be shadowed by the parameter"
    assert await stub.metadata() == "rpc-result"


@pytest.mark.asyncio
async def test_constructor_params_exposed_as_properties(requires_grpclib):
    from betterproto2.grpclib import ServiceStub

    channel = MockChannel()
    metadata = {"authorization": "token"}
    stub = ServiceStub(channel, timeout=12.5, metadata=metadata)

    assert stub.channel is channel
    assert stub.timeout == 12.5
    assert stub.deadline is None
    assert stub.metadata == metadata
