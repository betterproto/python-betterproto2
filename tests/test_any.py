def test_any() -> None:
    # TODO using a custom message pool will no longer be necessary when the well-known types will be compiled as well
    from tests.output_betterproto.any import Person
    from tests.output_betterproto.google.protobuf import Any

    person = Person(first_name="John", last_name="Smith")

    any = Any()
    any.pack(person)

    new_any = Any().parse(bytes(any))

    assert new_any.unpack() == person
