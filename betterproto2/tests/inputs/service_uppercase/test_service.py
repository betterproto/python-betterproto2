import inspect

from tests.util import requires_grpclib  # noqa: F401


def test_parameters(requires_grpclib):
    from tests.outputs.service_uppercase.service_uppercase import TestStub

    sig = inspect.signature(TestStub.do_thing)
    assert len(sig.parameters) == 5, "Expected 5 parameters"
