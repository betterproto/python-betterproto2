def test_any() -> None:
    # TODO using a custom message pool will no longer be necessary when the well-known types will be compiled as well
    from tests.output_betterproto.any import Person
    from tests.output_betterproto.google.protobuf import Any

    person = Person(first_name="John", last_name="Smith")

    any = Any()
    any.pack(person)

    new_any = Any.parse(bytes(any))

    assert new_any.unpack() == person


def test_any_to_dict() -> None:
    from tests.output_betterproto.any import Person
    from tests.output_betterproto.google.protobuf import Any

    person = Person(first_name="John", last_name="Smith")

    any = Any()

    # TODO test with include defautl value
    assert any.to_dict() == {"@type": ""}

    # Pack an object inside
    any.pack(person)

    assert any.to_dict() == {
        "@type": "type.googleapis.com/any.Person",
        "firstName": "John",
        "lastName": "Smith",
    }

    # Pack again in another Any
    any2 = Any()
    any2.pack(any)

    assert any2.to_dict() == {
        "@type": "type.googleapis.com/google.protobuf.Any",
        "value": {"@type": "type.googleapis.com/any.Person", "firstName": "John", "lastName": "Smith"},
    }
