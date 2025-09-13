from tests.util import requires_grpcio, requires_grpclib  # noqa: F401


def test_all_definition(requires_grpclib, requires_grpcio):
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
    assert enum.__all__ == (
        "ArithmeticOperator",
        "Choice",
        "EnumMessage",
        "HttpCode",
        "NewVersion",
        "NewVersionMessage",
        "NoStriping",
        "OldVersion",
        "OldVersionMessage",
        "Test",
    )
