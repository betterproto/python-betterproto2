def test_struct_to_dict():
    from tests.outputs.google.google.protobuf import Struct

    struct = Struct.from_dict(
        {
            "null_field": None,
            "number_field": 12,
            "string_field": "test",
            "bool_field": True,
            "struct_field": {"x": "abc"},
            "list_field": [42, False, None],
        }
    )

    assert struct.to_dict() == {
        "null_field": None,
        "number_field": 12,
        "string_field": "test",
        "bool_field": True,
        "struct_field": {"x": "abc"},
        "list_field": [42, False, None],
    }

    assert Struct.from_dict(struct.to_dict()) == struct


def test_listvalue_to_dict():
    from tests.outputs.google.google.protobuf import ListValue

    list_value = ListValue.from_dict([42, False, {}])

    assert list_value.to_dict() == [42, False, {}]
    assert ListValue.from_dict(list_value.to_dict()) == list_value


def test_nullvalue():
    from tests.outputs.google.google.protobuf import NullValue, Value

    null_value = NullValue.NULL_VALUE

    assert bytes(Value(null_value=null_value)) == b"\x08\x00"


def test_value_to_dict():
    from tests.outputs.google.google.protobuf import Value

    value = Value.from_dict([1, 2, False])

    assert value.to_dict() == [1, 2, False]
    assert Value.from_dict(value.to_dict()) == value
