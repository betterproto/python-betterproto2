"""Negative zero must survive serialization.

``-0.0`` compares equal to the ``0.0`` field default and is falsy, so it used to
be treated as unset and dropped from the binary wire format and from the
``to_dict`` / ``to_json`` output. The reference protobuf implementation keeps
``-0.0`` (its sign bit is set and distinguishes it from the default ``+0.0``), so
a round trip must preserve the sign.
"""

import math
from dataclasses import dataclass

import pytest

import betterproto2
from betterproto2 import OutputFormat


def _make_cls(proto_type: str):
    @dataclass(eq=False, repr=False)
    class Msg(betterproto2.Message):
        v: float = betterproto2.field(1, proto_type)

    return Msg


@pytest.mark.parametrize("proto_type", ["double", "float"])
def test_negative_zero_is_written_to_the_wire(proto_type):
    Msg = _make_cls(proto_type)

    wire = bytes(Msg(v=-0.0))
    assert wire, f"{proto_type} -0.0 was dropped from the binary output"

    back = Msg().parse(wire)
    assert back.v == 0.0
    assert math.copysign(1.0, back.v) == -1.0


@pytest.mark.parametrize("proto_type", ["double", "float"])
@pytest.mark.parametrize("output_format", [OutputFormat.PROTO_JSON, OutputFormat.PYTHON])
def test_negative_zero_is_kept_in_dict(proto_type, output_format):
    Msg = _make_cls(proto_type)

    as_dict = Msg(v=-0.0).to_dict(output_format=output_format)
    assert "v" in as_dict, f"{proto_type} -0.0 was dropped from {output_format} output"

    back = Msg().from_dict(as_dict)
    assert math.copysign(1.0, back.v) == -1.0


@pytest.mark.parametrize("proto_type", ["double", "float"])
def test_positive_zero_default_is_still_omitted(proto_type):
    # The actual default (+0.0) must keep being omitted everywhere.
    Msg = _make_cls(proto_type)
    assert bytes(Msg(v=0.0)) == b""
    assert Msg(v=0.0).to_dict(output_format=OutputFormat.PROTO_JSON) == {}
    assert Msg(v=0.0).to_dict(output_format=OutputFormat.PYTHON) == {}
