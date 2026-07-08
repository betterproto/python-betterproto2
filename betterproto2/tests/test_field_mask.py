from tests.outputs.google.google.protobuf import FieldMask


def test_to_dict_empty():
    assert FieldMask(paths=[]).to_dict() == ""


def test_to_dict_simple_paths():
    assert FieldMask(paths=["a", "b"]).to_dict() == "a,b"


def test_to_dict_camel_case_conversion():
    assert FieldMask(paths=["user.display_name", "photo"]).to_dict() == "user.displayName,photo"


def test_from_dict_string():
    mask = FieldMask.from_dict("user.displayName,photo")
    assert mask.paths == ["user.display_name", "photo"]


def test_from_dict_empty_string():
    mask = FieldMask.from_dict("")
    assert mask.paths == []
