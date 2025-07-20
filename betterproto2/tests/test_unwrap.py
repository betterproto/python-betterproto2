import pytest


def test_unwrap() -> None:
    from betterproto2 import unwrap
    from tests.outputs.unwrap.unwrap import Message, NestedMessage

    with pytest.raises(ValueError):
        unwrap(Message().x)

    msg = Message(x=NestedMessage())
    assert msg.x == unwrap(msg.x)
