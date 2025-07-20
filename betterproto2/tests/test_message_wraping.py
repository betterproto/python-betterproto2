import datetime


def test_message_wrapping_map():
    from tests.outputs.message_wrapping.message_wrapping import MapMessage

    msg = MapMessage(map1={"key": 12.0}, map2={"key": datetime.timedelta(seconds=1)})

    bytes(msg)

    assert msg.to_dict() == {"map1": {"key": 12.0}, "map2": {"key": "1s"}}
