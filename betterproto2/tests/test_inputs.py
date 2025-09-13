import copy
import importlib
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

import betterproto2
from tests.util import requires_grpcio, requires_grpclib, requires_protobuf, requires_pydantic  # noqa: F401

# Force pure-python implementation instead of C++, otherwise imports
# break things because we can't properly reset the symbol database.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


@dataclass
class TestCase:
    jsons: list[str]
    plugin_package: str
    reference_package: str
    reference_path: list[str] | None = None
    xfail: bool = False


def list_replace_nans(items: list) -> list[Any]:
    """Replace float("nan") in a list with the string "NaN"

    Parameters
    ----------
    items : List
            List to update

    Returns
    -------
    List[Any]
        Updated list
    """
    result = []
    for item in items:
        if isinstance(item, list):
            result.append(list_replace_nans(item))
        elif isinstance(item, dict):
            result.append(dict_replace_nans(item))
        elif isinstance(item, float) and math.isnan(item):
            result.append(betterproto2.NAN)
    return result


def dict_replace_nans(input_dict: dict[Any, Any]) -> dict[Any, Any]:
    """Replace float("nan") in a dictionary with the string "NaN"

    Parameters
    ----------
    input_dict : Dict[Any, Any]
            Dictionary to update

    Returns
    -------
    Dict[Any, Any]
        Updated dictionary
    """
    result = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            value = dict_replace_nans(value)
        elif isinstance(value, list):
            value = list_replace_nans(value)
        elif isinstance(value, float) and math.isnan(value):
            value = betterproto2.NAN
        result[key] = value
    return result


@pytest.fixture
def reset_sys_path():
    original = copy.deepcopy(sys.path)
    yield
    sys.path = original


TEST_CASES = [
    TestCase(["bool/bool.json"], "bool.bool", "bool_reference.bool_pb2"),
    TestCase(["bytes/bytes.json"], "bytes.bytes", "bytes_reference.bytes_pb2"),
    TestCase(["casing/casing.json"], "casing.casing", "casing_reference.casing_pb2"),
    TestCase(["deprecated/deprecated.json"], "deprecated.deprecated", "deprecated_reference.deprecated_pb2"),
    TestCase(["double/double.json", "double/double-negative.json"], "double.double", "double_reference.double_pb2"),
    TestCase(["enum/enum.json"], "enum.enum", "enum_reference.enum_pb2"),
    TestCase(
        ["field_name_identical_to_type/field_name_identical_to_type.json"],
        "field_name_identical_to_type.field_name_identical_to_type",
        "field_name_identical_to_type_reference.field_name_identical_to_type_pb2",
    ),
    TestCase(["fixed/fixed.json"], "fixed.fixed", "fixed_reference.fixed_pb2"),
    TestCase(["float/float.json"], "float.float", "float_reference.float_pb2"),
    TestCase(
        ["googletypes/googletypes.json", "googletypes/googletypes-missing.json"],
        "googletypes.googletypes",
        "googletypes_reference.googletypes_pb2",
    ),
    TestCase(
        ["googletypes_struct/googletypes_struct.json"],
        "googletypes_struct.googletypes_struct",
        "googletypes_struct_reference.googletypes_struct_pb2",
    ),
    TestCase(
        ["googletypes_value/googletypes_value.json"],
        "googletypes_value.googletypes_value",
        "googletypes_value_reference.googletypes_value_pb2",
    ),
    TestCase(["int32/int32.json"], "int32.int32", "int32_reference.int32_pb2"),
    TestCase(["map/map.json"], "map.map", "map_reference.map_pb2"),
    TestCase(["mapmessage/mapmessage.json"], "mapmessage.mapmessage", "mapmessage_reference.mapmessage_pb2"),
    TestCase(
        ["namespace_builtin_types/namespace_builtin_types.json"],
        "namespace_builtin_types.namespace_builtin_types",
        "namespace_builtin_types_reference.namespace_builtin_types_pb2",
    ),
    TestCase(
        ["namespace_keywords/namespace_keywords.json"],
        "namespace_keywords.namespace_keywords",
        "namespace_keywords_reference.namespace_keywords_pb2",
        xfail=True,
    ),
    TestCase(["nested/nested.json"], "nested.nested", "nested_reference.nested_pb2"),
    TestCase(["nestedtwice/nestedtwice.json"], "nestedtwice.nestedtwice", "nestedtwice_reference.nestedtwice_pb2"),
    TestCase(
        ["oneof_empty/oneof_empty.json", "oneof_empty/oneof_empty_maybe1.json", "oneof_empty/oneof_empty_maybe2.json"],
        "oneof_empty.oneof_empty",
        "oneof_empty_reference.oneof_empty_pb2",
    ),
    TestCase(
        ["oneof_enum/oneof_enum-enum-0.json", "oneof_enum/oneof_enum-enum-1.json", "oneof_enum/oneof_enum.json"],
        "oneof_enum.oneof_enum",
        "oneof_enum_reference.oneof_enum_pb2",
    ),
    TestCase(
        ["oneof/oneof.json", "oneof/oneof-name.json", "oneof/oneof_name.json"],
        "oneof.oneof",
        "oneof_reference.oneof_pb2",
    ),
    TestCase(
        ["proto3_field_presence_oneof/proto3_field_presence_oneof.json"],
        "proto3_field_presence_oneof.proto3_field_presence_oneof",
        "proto3_field_presence_oneof_reference.proto3_field_presence_oneof_pb2",
    ),
    TestCase(
        [
            "proto3_field_presence/proto3_field_presence_default.json",
            "proto3_field_presence/proto3_field_presence.json",
            "proto3_field_presence/proto3_field_presence_missing.json",
        ],
        "proto3_field_presence.proto3_field_presence",
        "proto3_field_presence_reference.proto3_field_presence_pb2",
    ),
    TestCase(
        ["recursivemessage/recursivemessage.json"],
        "recursivemessage.recursivemessage",
        "recursivemessage_reference.recursivemessage_pb2",
    ),
    TestCase(["ref/ref.json"], "ref.ref", "ref_reference.ref_pb2", reference_path=["ref_reference"]),
    TestCase(
        ["repeated_duration_timestamp/repeated_duration_timestamp.json"],
        "repeated_duration_timestamp.repeated_duration_timestamp",
        "repeated_duration_timestamp_reference.repeated_duration_timestamp_pb2",
    ),
    TestCase(
        ["repeatedmessage/repeatedmessage.json"],
        "repeatedmessage.repeatedmessage",
        "repeatedmessage_reference.repeatedmessage_pb2",
    ),
    TestCase(
        ["repeatedpacked/repeatedpacked.json"],
        "repeatedpacked.repeatedpacked",
        "repeatedpacked_reference.repeatedpacked_pb2",
    ),
    TestCase(["repeated/repeated.json"], "repeated.repeated", "repeated_reference.repeated_pb2"),
    TestCase(["signed/signed.json"], "signed.signed", "signed_reference.signed_pb2"),
    TestCase(
        ["timestamp_dict_encode/timestamp_dict_encode.json"],
        "timestamp_dict_encode.timestamp_dict_encode",
        "timestamp_dict_encode_reference.timestamp_dict_encode_pb2",
    ),
]


@pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x.plugin_package)
def test_message_json(test_case: TestCase, requires_pydantic, requires_grpcio, requires_grpclib) -> None:
    if test_case.xfail:
        pytest.xfail(f"Test case {test_case.plugin_package} is expected to fail.")

    plugin_module = importlib.import_module(f"tests.outputs.{test_case.plugin_package}")

    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    for json_path in test_case.jsons:
        with open(current_dir / "inputs" / json_path) as f:
            json_data = f.read()

        message: betterproto2.Message = plugin_module.Test.from_json(json_data)
        message_json = message.to_json(indent=0)

        assert dict_replace_nans(json.loads(message_json)) == dict_replace_nans(json.loads(json_data))


@pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda x: x.plugin_package)
def test_binary_compatibility(
    test_case: TestCase, reset_sys_path, requires_grpcio, requires_protobuf, requires_grpclib
) -> None:
    from google.protobuf.json_format import Parse

    if test_case.xfail:
        pytest.xfail(f"Test case {test_case.plugin_package} is expected to fail.")

    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    if test_case.reference_path:
        for path in test_case.reference_path:
            sys.path.append(str(current_dir / "outputs" / path))

    plugin_module = importlib.import_module(f"tests.outputs.{test_case.plugin_package}")
    reference_module = importlib.import_module(f"tests.outputs.{test_case.reference_package}")

    # TODO fix and delete
    if "map" in plugin_module.__file__.replace("\\", "/").split("/"):
        pytest.skip("Skipping this test for now.")

    for json_path in test_case.jsons:
        with open(current_dir / "inputs" / json_path) as f:
            json_data = f.read()

        reference_instance = Parse(json_data, reference_module.Test())
        reference_binary_output = reference_instance.SerializeToString()

        plugin_instance_from_json: betterproto2.Message = plugin_module.Test().from_json(json_data)
        plugin_instance_from_binary = plugin_module.Test.FromString(reference_binary_output)

        # Generally this can't be relied on, but here we are aiming to match the
        # existing Python implementation and aren't doing anything tricky.
        # https://developers.google.com/protocol-buffers/docs/encoding#implications
        assert bytes(plugin_instance_from_json) == reference_binary_output
        assert bytes(plugin_instance_from_binary) == reference_binary_output

        assert plugin_instance_from_json == plugin_instance_from_binary
        assert dict_replace_nans(plugin_instance_from_json.to_dict()) == dict_replace_nans(
            plugin_instance_from_binary.to_dict()
        )
