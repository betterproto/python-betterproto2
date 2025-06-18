import pytest

from tests.output_betterproto.import_cousin_package_same_name.test.subpackage import Test

# importing the cousin should cause no descriptor pool errors since the subpackage imports it once already
from tests.output_betterproto_descriptor.import_cousin_package_same_name.cousin.subpackage import CousinMessage
from tests.output_betterproto_descriptor.import_cousin_package_same_name.test.subpackage import Test as TestWithDesc


def test_message_enum_descriptors():
    # Normally descriptors are not available as they require protobuf support
    # to inteoperate with other libraries.
    with pytest.raises(AttributeError):
        Test.DESCRIPTOR.full_name

    # But the python_betterproto2_opt=google_protobuf_descriptors option
    # will add them in as long as protobuf is depended on.
    assert TestWithDesc.DESCRIPTOR.full_name == "import_cousin_package_same_name.test.subpackage.Test"
    assert CousinMessage.DESCRIPTOR.full_name == "import_cousin_package_same_name.cousin.subpackage.CousinMessage"
