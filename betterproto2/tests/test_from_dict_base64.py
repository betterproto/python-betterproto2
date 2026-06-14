"""``from_dict`` must accept URL-safe base64 for ``bytes`` fields.

The proto3 JSON mapping accepts a ``bytes`` value encoded with either the
standard or the URL-safe base64 alphabet, with or without padding. The
reference protobuf implementation decodes all of these forms; betterproto2 used
plain ``base64.b64decode``, which only understands the standard alphabet and
*silently* discards the URL-safe ``-``/``_`` characters, so a URL-safe payload
decoded to the wrong (often empty) bytes instead of raising or round-tripping.
"""

import base64
from dataclasses import dataclass

import pytest

import betterproto2


def _make_cls():
    @dataclass(eq=False, repr=False)
    class Msg(betterproto2.Message):
        v: bytes = betterproto2.field(1, "bytes")

    return Msg


# Bytes whose standard base64 contains both '+' and '/', so the URL-safe form
# differs in both substituted characters.
RAW = b"\xfb\xef\xff\x01"


def _encodings(raw: bytes):
    std = base64.b64encode(raw).decode()
    url = base64.urlsafe_b64encode(raw).decode()
    return {
        "standard_padded": std,
        "standard_unpadded": std.rstrip("="),
        "urlsafe_padded": url,
        "urlsafe_unpadded": url.rstrip("="),
    }


@pytest.mark.parametrize("form", ["standard_padded", "standard_unpadded", "urlsafe_padded", "urlsafe_unpadded"])
def test_from_dict_accepts_every_base64_form(form):
    Msg = _make_cls()
    encoded = _encodings(RAW)[form]

    decoded = Msg().from_dict({"v": encoded}).v

    assert decoded == RAW, f"{form} base64 {encoded!r} decoded to {decoded!r}"


def test_to_dict_from_dict_bytes_round_trip():
    Msg = _make_cls()

    as_dict = Msg(v=RAW).to_dict()
    assert Msg().from_dict(as_dict).v == RAW
