from dataclasses import dataclass
from typing import Optional

import pytest

import betterproto2


def test_oneof_pattern_matching():
    @dataclass
    class Sub(betterproto2.Message):
        val: int = betterproto2.int32_field(1)

    @dataclass
    class Foo(betterproto2.Message):
        bar: Optional[int] = betterproto2.int32_field(1, group="group1")
        baz: Optional[str] = betterproto2.string_field(2, group="group1")
        sub: Optional[Sub] = betterproto2.message_field(3, group="group2")
        abc: Optional[str] = betterproto2.string_field(4, group="group2")

    foo = Foo(baz="test1", abc="test2")

    match foo:
        case Foo(bar=int(_)):
            pytest.fail("Matched 'bar' instead of 'baz'")
        case Foo(baz=v):
            assert v == "test1"
        case _:
            pytest.fail("Matched neither 'bar' nor 'baz'")

    match foo:
        case Foo(sub=Sub(_)):
            pytest.fail("Matched 'sub' instead of 'abc'")
        case Foo(abc=v):
            assert v == "test2"
        case _:
            pytest.fail("Matched neither 'sub' nor 'abc'")

    foo.sub = Sub(val=1)

    match foo:
        case Foo(sub=Sub(val=v)):
            assert v == 1
        case Foo(abc=str(v)):
            pytest.fail("Matched 'abc' instead of 'sub'")
        case _:
            pytest.fail("Matched neither 'sub' nor 'abc'")
