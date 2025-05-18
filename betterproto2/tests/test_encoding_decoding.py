def test_int_overflow():
    """Make sure that overflows in encoded values are handled correctly."""
    from tests.output_betterproto_pydantic.encoding_decoding import Overflow32, Overflow64

    b = bytes(Overflow64(uint=2**50 + 42))
    msg = Overflow32.parse(b)
    assert msg.uint == 42

    b = bytes(Overflow64(int=2**50 + 42))
    msg = Overflow32.parse(b)
    assert msg.int == 42

    b = bytes(Overflow64(int=2**50 - 42))
    msg = Overflow32.parse(b)
    assert msg.int == -42

    b = bytes(Overflow64(sint=2**50 + 42))
    msg = Overflow32.parse(b)
    assert msg.sint == 42

    b = bytes(Overflow64(sint=-(2**50) - 42))
    msg = Overflow32.parse(b)
    assert msg.sint == -42
