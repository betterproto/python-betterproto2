import pytest

from tests.util import requires_protobuf  # noqa: F401


def test_message_enum_descriptors(requires_protobuf):
    from tests.outputs.import_cousin_package_same_name.import_cousin_package_same_name.test.subpackage import Test

    # importing the cousin should cause no descriptor pool errors since the subpackage imports it once already
    from tests.outputs.import_cousin_package_same_name_descriptors.import_cousin_package_same_name.cousin.subpackage import (  # noqa: E501
        CousinMessage,
    )
    from tests.outputs.import_cousin_package_same_name_descriptors.import_cousin_package_same_name.test.subpackage import (  # noqa: E501
        Test as TestWithDesc,
    )

    # Normally descriptors are not available as they require protobuf support
    # to inteoperate with other libraries.
    with pytest.raises(AttributeError):
        Test.DESCRIPTOR.full_name

    # But the python_betterproto2_opt=google_protobuf_descriptors option
    # will add them in as long as protobuf is depended on.
    assert TestWithDesc.DESCRIPTOR.full_name == "import_cousin_package_same_name.test.subpackage.Test"
    assert CousinMessage.DESCRIPTOR.full_name == "import_cousin_package_same_name.cousin.subpackage.CousinMessage"
