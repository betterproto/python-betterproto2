def test_all_definition():
    """
    Check that a compiled module defines __all__ with the right value.

    These modules have been chosen since they contain messages, services and enums.
    """
    import tests.outputs.enum.enum as enum
    import tests.outputs.service.service as service

    assert service.__all__ == (
        "DoThingRequest",
        "DoThingResponse",
        "GetThingRequest",
        "GetThingResponse",
        "TestBase",
        "TestStub",
        "TestSyncStub",
        "ThingType",
    )
    assert enum.__all__ == ("ArithmeticOperator", "Choice", "EnumMessage", "HttpCode", "NoStriping", "Test")
