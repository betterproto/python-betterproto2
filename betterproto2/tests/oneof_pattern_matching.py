import pytest


def test_oneof_pattern_matching():
    from tests.output_betterproto.features import IntMsg, OneofMsg

    msg = OneofMsg(y="test1", b="test2")

    match msg:
        case OneofMsg(x=int(_)):
            pytest.fail("Matched 'bar' instead of 'baz'")
        case OneofMsg(y=v):
            assert v == "test1"
        case _:
            pytest.fail("Matched neither 'bar' nor 'baz'")

    match msg:
        case OneofMsg(a=IntMsg(_)):
            pytest.fail("Matched 'sub' instead of 'abc'")
        case OneofMsg(b=v):
            assert v == "test2"
        case _:
            pytest.fail("Matched neither 'sub' nor 'abc'")

    msg.b = None
    msg.a = IntMsg(val=1)

    match msg:
        case OneofMsg(a=IntMsg(val=v)):
            assert v == 1
        case OneofMsg(b=str(v)):
            pytest.fail("Matched 'abc' instead of 'sub'")
        case _:
            pytest.fail("Matched neither 'sub' nor 'abc'")
