def test_any() -> None:
    # TODO using a custom message pool will no longer be necessary when the well-known types will be compiled as well
    from betterproto2.lib.google.protobuf import Any
    from tests.output_betterproto.any import Person
    from tests.output_betterproto.message_pool import default_message_pool

    person = Person(first_name="John", last_name="Smith")

    any = Any()
    any.pack(person, message_pool=default_message_pool)

    new_any = Any().parse(bytes(any))

    assert new_any.unpack(message_pool=default_message_pool) == person
