def test_nested_from_dict():
    """
    Make sure that from_dict() arguments are passed recursively
    """
    from tests.outputs.nested.nested import Test

    data = {
        "nested": {"count": 1},
        "sibling": {"foo": 2},
    }
    Test.from_dict(data)

    data["bar"] = 3
    Test.from_dict(data, ignore_unknown_fields=True)

    data["nested"]["bar"] = 3
    Test.from_dict(data, ignore_unknown_fields=True)

    data["sibling"]["bar"] = 4
    Test.from_dict(data, ignore_unknown_fields=True)
