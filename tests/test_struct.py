def test_struct_to_dict():
    from tests.output_betterproto_pydantic.google.protobuf import ListValue, NullValue, Struct, Value

    struct = Struct(
        fields={
            "null_field": Value(null_value=NullValue._),  # TODO fix the name
            "number_field": Value(number_value=12),
            "string_field": Value(string_value="test"),
            "bool_field": Value(bool_value=True),
            "struct_field": Value(struct_value=Struct(fields={"x": Value(string_value="abc")})),
            "list_field": Value(list_value=ListValue(values=[Value(number_value=42), Value(bool_value=False)])),
        }
    )

    assert struct.to_dict() == {
        "null_field": None,
        "number_field": 12,
        "string_field": "test",
        "bool_field": True,
        "struct_field": {"x": "abc"},
        "list_field": [42, False],
    }
