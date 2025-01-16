def test_any() -> None:
    from betterproto2.lib.google.protobuf import Any
    from tests.output_betterproto.any import Person

    person = Person(first_name="John", last_name="Smith")

    any = Any()
    any.pack(person)

    new_any = Any().parse(bytes(any))

    assert new_any.unpack() == person
