import pickle
from copy import (
    copy,
    deepcopy,
)
from dataclasses import dataclass
from typing import (
    Dict,
    List,
)

import cachelib

import betterproto2
from betterproto2.lib.google import protobuf as google


def unpickled(message):
    return pickle.loads(pickle.dumps(message))


@dataclass(eq=False, repr=False)
class Fe(betterproto2.Message):
    abc: str = betterproto2.string_field(1)


@dataclass(eq=False, repr=False)
class Fi(betterproto2.Message):
    abc: str = betterproto2.string_field(1)


@dataclass(eq=False, repr=False)
class Fo(betterproto2.Message):
    abc: str = betterproto2.string_field(1)


@dataclass(eq=False, repr=False)
class NestedData(betterproto2.Message):
    struct_foo: Dict[str, "google.Struct"] = betterproto2.map_field(
        1, betterproto2.TYPE_STRING, betterproto2.TYPE_MESSAGE
    )
    map_str_any_bar: Dict[str, "google.Any"] = betterproto2.map_field(
        2, betterproto2.TYPE_STRING, betterproto2.TYPE_MESSAGE
    )


@dataclass(eq=False, repr=False)
class Complex(betterproto2.Message):
    foo_str: str = betterproto2.string_field(1)
    fe: "Fe" = betterproto2.message_field(3, group="grp")
    fi: "Fi" = betterproto2.message_field(4, group="grp")
    fo: "Fo" = betterproto2.message_field(5, group="grp")
    nested_data: "NestedData" = betterproto2.message_field(6)
    mapping: Dict[str, "google.Any"] = betterproto2.map_field(7, betterproto2.TYPE_STRING, betterproto2.TYPE_MESSAGE)


def complex_msg():
    return Complex(
        foo_str="yep",
        fe=Fe(abc="1"),
        nested_data=NestedData(
            struct_foo={
                "foo": google.Struct(
                    fields={
                        "hello": google.Value(list_value=google.ListValue(values=[google.Value(string_value="world")]))
                    }
                ),
            },
            map_str_any_bar={
                "key": google.Any(value=b"value"),
            },
        ),
        mapping={
            "message": google.Any(value=bytes(Fi(abc="hi"))),
            "string": google.Any(value=b"howdy"),
        },
    )


def test_pickling_complex_message():
    msg = complex_msg()
    deser = unpickled(msg)
    assert msg == deser
    assert msg.fe.abc == "1"
    assert msg.is_set("fi") is not True
    assert msg.mapping["message"] == google.Any(value=bytes(Fi(abc="hi")))
    assert msg.mapping["string"].value.decode() == "howdy"
    assert msg.nested_data.struct_foo["foo"].fields["hello"].list_value.values[0].string_value == "world"


def test_recursive_message_defaults():
    from tests.output_betterproto.recursivemessage import (
        Intermediate,
        Test as RecursiveMessage,
    )

    msg = RecursiveMessage(name="bob", intermediate=Intermediate(42))
    msg = unpickled(msg)

    # set values are as expected
    assert msg == RecursiveMessage(name="bob", intermediate=Intermediate(42))

    # lazy initialized works modifies the message
    assert msg != RecursiveMessage(name="bob", intermediate=Intermediate(42), child=RecursiveMessage(name="jude"))
    msg.child = RecursiveMessage(child=RecursiveMessage(name="jude"))
    assert msg == RecursiveMessage(
        name="bob",
        intermediate=Intermediate(42),
        child=RecursiveMessage(child=RecursiveMessage(name="jude")),
    )


@dataclass
class PickledMessage(betterproto2.Message):
    foo: bool = betterproto2.bool_field(1)
    bar: int = betterproto2.int32_field(2)
    baz: List[str] = betterproto2.string_field(3, repeated=True)


def test_copyability():
    msg = PickledMessage(bar=12, baz=["hello"])
    msg = unpickled(msg)

    copied = copy(msg)
    assert msg == copied
    assert msg is not copied
    assert msg.baz is copied.baz

    deepcopied = deepcopy(msg)
    assert msg == deepcopied
    assert msg is not deepcopied
    assert msg.baz is not deepcopied.baz


def test_message_can_be_cached():
    """Cachelib uses pickling to cache values"""

    cache = cachelib.SimpleCache()

    def use_cache():
        calls = getattr(use_cache, "calls", 0)
        result = cache.get("message")
        if result is not None:
            return result
        else:
            setattr(use_cache, "calls", calls + 1)
            result = complex_msg()
            cache.set("message", result)
            return result

    for n in range(10):
        if n == 0:
            assert not cache.has("message")
        else:
            assert cache.has("message")

        msg = use_cache()
        assert use_cache.calls == 1  # The message is only ever built once
        assert msg.fe.abc == "1"
        assert msg.is_set("fi") is not True
        assert msg.mapping["message"] == google.Any(value=bytes(Fi(abc="hi")))
        assert msg.mapping["string"].value.decode() == "howdy"
        assert msg.nested_data.struct_foo["foo"].fields["hello"].list_value.values[0].string_value == "world"
