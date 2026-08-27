from enum import IntEnum
from types import SimpleNamespace

from pydantic.dataclasses import dataclass

import betterproto2


@dataclass(eq=False, repr=False)
class GeneratedMessage(betterproto2.Message):
    # This mirrors python-betterproto2 output where a direct child package is
    # imported as ``data`` after the class declarations.
    namespace: "data.GeneratedNamespace" = betterproto2.field(
        1,
        betterproto2.TYPE_ENUM,
        default_factory=lambda: data.GeneratedNamespace(0),
    )


class GeneratedNamespace(IntEnum):
    UNKNOWN = 0


data = SimpleNamespace(GeneratedNamespace=GeneratedNamespace)


def test_pydantic_forward_reference_resolves_on_cold_parse():
    assert GeneratedMessage.parse(b"").namespace is GeneratedNamespace.UNKNOWN


def test_pydantic_forward_reference_resolves_for_keyword_data_argument():
    assert GeneratedMessage.parse(data=b"").namespace is GeneratedNamespace.UNKNOWN
