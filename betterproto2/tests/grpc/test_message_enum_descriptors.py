import pytest

from tests.output_betterproto.service import ThingType, DoThingRequest
from tests.output_betterproto_descriptor.service import ThingType as ThingTypeWithDesc, DoThingRequest as DoThingRequestWithDesc

def test_message_enum_descriptors():
    # Normally descriptors are not available as they require protobuf support
    # to inteoperate with other libraries.
    with pytest.raises(AttributeError):
        ThingType.DESCRIPTOR.full_name
    with pytest.raises(AttributeError):
        DoThingRequest.DESCRIPTOR.full_name

    # But the python_betterproto2_opt=google_protobuf_descriptors option
    # will add them in as long as protobuf is depended on.
    assert ThingTypeWithDesc.DESCRIPTOR.full_name == "service.ThingType"
    assert DoThingRequestWithDesc.DESCRIPTOR.full_name == "service.DoThingRequest"
