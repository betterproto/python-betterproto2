import json
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from inspect import (
    Parameter,
    signature,
)
from unittest.mock import ANY

import pytest

import betterproto2
from betterproto2 import OutputFormat


def test_class_init():
    from tests.output_betterproto.features import Bar, Foo

    foo = Foo(name="foo", child=Bar(name="bar"))

    assert foo.to_dict() == {"name": "foo", "child": {"name": "bar"}}
    assert foo.to_dict(output_format=OutputFormat.PYTHON) == {"name": "foo", "child": {"name": "bar"}}


def test_enum_as_int_json():
    from tests.output_betterproto.features import Enum, EnumMsg

    # JSON strings are supported, but ints should still be supported too.
    enum_msg = EnumMsg().from_dict({"enum": 1})
    assert enum_msg.enum == Enum.ONE

    # Plain-ol'-ints should serialize properly too.
    enum_msg.enum = 1
    assert enum_msg.to_dict() == {"enum": "ONE"}

    # Similar expectations for pydict
    enum_msg = EnumMsg().from_dict({"enum": 1})
    assert enum_msg.enum == Enum.ONE
    assert enum_msg.to_dict(output_format=OutputFormat.PYTHON) == {"enum": Enum.ONE}


def test_unknown_fields():
    from tests.output_betterproto.features import Newer, Older

    newer = Newer(x=True, y=1, z="Hello")
    serialized_newer = bytes(newer)

    # Unknown fields in `Newer` should round trip with `Older`
    round_trip = bytes(Older.parse(serialized_newer))
    assert serialized_newer == round_trip

    new_again = Newer.parse(round_trip)
    assert newer == new_again


def test_from_dict_unknown_fields():
    from tests.output_betterproto.features import Older

    with pytest.raises(KeyError):
        Older.from_dict({"x": True, "y": 1})

    assert Older.from_dict({"x": True, "y": 1}, ignore_unknown_fields=True) == Older(x=True)


def test_from_json_unknown_fields():
    from tests.output_betterproto.features import Older

    with pytest.raises(KeyError):
        Older.from_json('{"x": true, "y": 1}')

    assert Older.from_json('{"x": true, "y": 1}', ignore_unknown_fields=True) == Older(x=True)


def test_oneof_support():
    from tests.output_betterproto.features import IntMsg, OneofMsg

    msg = OneofMsg()

    assert betterproto2.which_one_of(msg, "group1")[0] == ""

    msg.x = 1
    assert betterproto2.which_one_of(msg, "group1")[0] == "x"

    msg.x = None
    msg.y = "test"
    assert betterproto2.which_one_of(msg, "group1")[0] == "y"

    msg.a = IntMsg(val=1)
    assert betterproto2.which_one_of(msg, "group2")[0] == "a"

    msg.a = None
    msg.b = "test"
    assert betterproto2.which_one_of(msg, "group2")[0] == "b"

    # Group 1 shouldn't be touched
    assert betterproto2.which_one_of(msg, "group1")[0] == "y"

    # Zero value should always serialize for one-of
    msg = OneofMsg(x=0)
    assert betterproto2.which_one_of(msg, "group1")[0] == "x"
    assert bytes(msg) == b"\x08\x00"

    # Round trip should also work
    msg = OneofMsg.parse(bytes(msg))
    assert betterproto2.which_one_of(msg, "group1")[0] == "x"
    assert msg.x == 0
    assert betterproto2.which_one_of(msg, "group2")[0] == ""


def test_json_casing():
    from tests.output_betterproto.features import JsonCasingMsg

    # Parsing should accept almost any input
    msg = JsonCasingMsg().from_dict({"PascalCase": 1, "camelCase": 2, "snake_case": 3, "kabob-case": 4})

    assert msg == JsonCasingMsg(1, 2, 3, 4)

    # Serializing should be strict.
    assert json.loads(msg.to_json()) == {
        "pascalCase": 1,
        "camelCase": 2,
        "snakeCase": 3,
        "kabobCase": 4,
    }

    assert json.loads(msg.to_json(casing=betterproto2.Casing.SNAKE)) == {
        "pascal_case": 1,
        "camel_case": 2,
        "snake_case": 3,
        "kabob_case": 4,
    }


def test_dict_casing():
    from tests.output_betterproto.features import JsonCasingMsg

    # Parsing should accept almost any input
    msg = JsonCasingMsg().from_dict({"PascalCase": 1, "camelCase": 2, "snake_case": 3, "kabob-case": 4})

    assert msg == JsonCasingMsg(1, 2, 3, 4)

    # Serializing should be strict.
    assert msg.to_dict() == {
        "pascalCase": 1,
        "camelCase": 2,
        "snakeCase": 3,
        "kabobCase": 4,
    }

    assert msg.to_dict(casing=betterproto2.Casing.SNAKE) == {
        "pascal_case": 1,
        "camel_case": 2,
        "snake_case": 3,
        "kabob_case": 4,
    }


def test_optional_flag():
    from tests.output_betterproto.features import OptionalBoolMsg

    # Serialization of not passed vs. set vs. zero-value.
    assert bytes(OptionalBoolMsg()) == b""
    assert bytes(OptionalBoolMsg(field=True)) == b"\n\x02\x08\x01"
    assert bytes(OptionalBoolMsg(field=False)) == b"\n\x00"

    # Differentiate between not passed and the zero-value.
    assert OptionalBoolMsg.parse(b"").field is None
    assert OptionalBoolMsg.parse(b"\n\x00").field is False


def test_optional_datetime_to_dict():
    from tests.output_betterproto.features import OptionalDatetimeMsg

    # Check dict serialization
    assert OptionalDatetimeMsg().to_dict() == {}
    assert OptionalDatetimeMsg().to_dict(include_default_values=True) == {"field": None}
    assert OptionalDatetimeMsg(field=datetime(2020, 1, 1, tzinfo=timezone.utc)).to_dict() == {
        "field": "2020-01-01T00:00:00Z"
    }
    assert OptionalDatetimeMsg(field=datetime(2020, 1, 1, tzinfo=timezone.utc)).to_dict(
        include_default_values=True
    ) == {"field": "2020-01-01T00:00:00Z"}

    # Check pydict serialization
    assert OptionalDatetimeMsg().to_dict(output_format=OutputFormat.PYTHON) == {}
    assert OptionalDatetimeMsg().to_dict(include_default_values=True, output_format=OutputFormat.PYTHON) == {
        "field": None
    }
    assert OptionalDatetimeMsg(field=datetime(2020, 1, 1)).to_dict(output_format=OutputFormat.PYTHON) == {
        "field": datetime(2020, 1, 1)
    }
    assert OptionalDatetimeMsg(field=datetime(2020, 1, 1)).to_dict(
        include_default_values=True, output_format=OutputFormat.PYTHON
    ) == {"field": datetime(2020, 1, 1)}


def test_to_json_default_values():
    from tests.output_betterproto.features import MsgA

    # Empty dict
    test = MsgA().from_dict({})

    assert json.loads(test.to_json(include_default_values=True)) == {
        "someInt": 0,
        "someDouble": 0.0,
        "someStr": "",
        "someBool": False,
    }

    # All default values
    test = MsgA().from_dict({"someInt": 0, "someDouble": 0.0, "someStr": "", "someBool": False})

    assert json.loads(test.to_json(include_default_values=True)) == {
        "someInt": 0,
        "someDouble": 0.0,
        "someStr": "",
        "someBool": False,
    }


def test_to_dict_default_values():
    from tests.output_betterproto.features import MsgA, MsgB

    # Empty dict
    test = MsgA()

    assert test.to_dict(include_default_values=True) == {
        "someInt": 0,
        "someDouble": 0.0,
        "someStr": "",
        "someBool": False,
    }

    assert test.to_dict(include_default_values=True, output_format=OutputFormat.PYTHON) == {
        "someInt": 0,
        "someDouble": 0.0,
        "someStr": "",
        "someBool": False,
    }

    # Some default and some other values
    test = MsgB().from_dict(
        {
            "someInt": 2,
            "someDouble": 1.2,
            "someStr": "hello",
            "someBool": True,
            "someDefaultInt": 0,
            "someDefaultDouble": 0.0,
            "someDefaultStr": "",
            "someDefaultBool": False,
        }
    )

    assert test.to_dict(include_default_values=True) == {
        "someInt": 2,
        "someDouble": 1.2,
        "someStr": "hello",
        "someBool": True,
        "someDefaultInt": 0,
        "someDefaultDouble": 0.0,
        "someDefaultStr": "",
        "someDefaultBool": False,
    }


def test_to_dict_datetime_values():
    from tests.output_betterproto.features import TimeMsg

    test = TimeMsg.from_dict({"timestamp": "2020-01-01T00:00:00Z", "duration": "86400s"})
    assert test.to_dict() == {"timestamp": "2020-01-01T00:00:00Z", "duration": "86400s"}

    test = TimeMsg.from_dict(
        {"timestamp": datetime(year=2020, month=1, day=1, tzinfo=timezone.utc), "duration": timedelta(days=1)}
    )
    assert test.to_dict(output_format=OutputFormat.PYTHON) == {
        "timestamp": datetime(year=2020, month=1, day=1, tzinfo=timezone.utc),
        "duration": timedelta(days=1),
    }
    assert test.to_dict(output_format=OutputFormat.PROTO_JSON) == {
        "timestamp": "2020-01-01T00:00:00Z",
        "duration": "86400s",
    }
    bytes(test)


def test_oneof_default_value_set_causes_writes_wire():
    from tests.output_betterproto.features import Empty, MsgC

    def _round_trip_serialization(msg: MsgC) -> MsgC:
        return MsgC.parse(bytes(msg))

    int_msg = MsgC(int_field=0)
    str_msg = MsgC(string_field="")
    empty_msg = MsgC(empty_field=Empty())
    msg = MsgC()

    assert bytes(int_msg) == b"\x08\x00"
    assert (
        betterproto2.which_one_of(int_msg, "group1")
        == betterproto2.which_one_of(_round_trip_serialization(int_msg), "group1")
        == ("int_field", 0)
    )

    assert bytes(str_msg) == b"\x12\x00"  # Baz is just an empty string
    assert (
        betterproto2.which_one_of(str_msg, "group1")
        == betterproto2.which_one_of(_round_trip_serialization(str_msg), "group1")
        == ("string_field", "")
    )

    assert bytes(empty_msg) == b"\x1a\x00"
    assert (
        betterproto2.which_one_of(empty_msg, "group1")
        == betterproto2.which_one_of(_round_trip_serialization(empty_msg), "group1")
        == ("empty_field", Empty())
    )

    assert bytes(msg) == b""
    assert (
        betterproto2.which_one_of(msg, "group1")
        == betterproto2.which_one_of(_round_trip_serialization(msg), "group1")
        == ("", None)
    )


def test_message_repr():
    from tests.output_betterproto.recursivemessage import Test

    assert repr(Test(name="Loki")) == "Test(name='Loki')"
    assert repr(Test(child=Test(), name="Loki")) == "Test(name='Loki', child=Test())"


def test_bool():
    """Messages should evaluate similarly to a collection
    >>> test = []
    >>> bool(test)
    ... False
    >>> test.append(1)
    >>> bool(test)
    ... True
    >>> del test[0]
    >>> bool(test)
    ... False
    """
    from tests.output_betterproto.features import Empty, IntMsg

    assert not Empty()
    t = IntMsg()
    assert not t
    t.val = 1
    assert t
    t.val = 0
    assert not t


# valid ISO datetimes according to https://www.myintervals.com/blog/2009/05/20/iso-8601-date-validation-that-doesnt-suck/
iso_candidates = """2009-12-12T12:34
2009
2009-05-19
2009-05-19
20090519
2009123
2009-05
2009-123
2009-222
2009-001
2009-W01-1
2009-W51-1
2009-W33
2009W511
2009-05-19
2009-05-19 00:00
2009-05-19 14
2009-05-19 14:31
2009-05-19 14:39:22
2009-05-19T14:39Z
2009-W21-2
2009-W21-2T01:22
2009-139
2009-05-19 14:39:22-06:00
2009-05-19 14:39:22+0600
2009-05-19 14:39:22-01
20090621T0545Z
2007-04-06T00:00
2007-04-05T24:00
2010-02-18T16:23:48.5
2010-02-18T16:23:48,444
2010-02-18T16:23:48,3-06:00
2010-02-18T16:23:00.4
2010-02-18T16:23:00,25
2010-02-18T16:23:00.33+0600
2010-02-18T16:00:00.23334444
2010-02-18T16:00:00,2283
2009-05-19 143922
2009-05-19 1439""".split("\n")


def test_iso_datetime():
    from tests.output_betterproto.features import TimeMsg

    for _, candidate in enumerate(iso_candidates):
        msg = TimeMsg.from_dict({"timestamp": candidate})
        assert isinstance(msg.timestamp, datetime)


def test_iso_datetime_list():
    from tests.output_betterproto.features import MsgD

    msg = MsgD()

    msg.from_dict({"timestamps": iso_candidates})
    assert all([isinstance(item, datetime) for item in msg.timestamps])


def test_service_argument__expected_parameter():
    from tests.output_betterproto.service import TestStub

    sig = signature(TestStub.do_thing)
    do_thing_request_parameter = sig.parameters["message"]
    assert do_thing_request_parameter.default is Parameter.empty
    assert do_thing_request_parameter.annotation == "DoThingRequest"


def test_is_set():
    from tests.output_betterproto.features import MsgE

    assert not MsgE().is_set("bool_field")
    assert not MsgE().is_set("int_field")
    assert MsgE(bool_field=True).is_set("bool_field")
    assert MsgE(bool_field=True, int_field=0).is_set("int_field")


def test_equality_comparison():
    from tests.output_betterproto.bool import Test as TestMessage

    msg = TestMessage(value=True)

    assert msg == msg
    assert msg == ANY
    assert msg == TestMessage(value=True)
    assert msg != 1
    assert msg != TestMessage(value=False)
