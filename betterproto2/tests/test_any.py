def test_any() -> None:
    from tests.outputs.any.any import Person
    from tests.outputs.any.google.protobuf import Any

    person = Person(first_name="John", last_name="Smith")

    any = Any.pack(person)

    new_any = Any.parse(bytes(any))

    assert new_any.unpack() == person


def test_any_to_dict() -> None:
    from tests.outputs.any.any import Person
    from tests.outputs.any.google.protobuf import Any

    person = Person(first_name="John", last_name="Smith")

    # TODO test with include defautl value
    assert Any().to_dict() == {"@type": ""}

    # Pack an object inside
    any = Any.pack(person)

    assert any.to_dict() == {
        "@type": "type.googleapis.com/any.Person",
        "firstName": "John",
        "lastName": "Smith",
    }

    assert Any.from_dict(any.to_dict()) == any

    # Pack again in another Any
    any2 = Any.pack(any)

    assert any2.to_dict() == {
        "@type": "type.googleapis.com/google.protobuf.Any",
        "value": {"@type": "type.googleapis.com/any.Person", "firstName": "John", "lastName": "Smith"},
    }

    assert Any.from_dict(any2.to_dict()) == any2
