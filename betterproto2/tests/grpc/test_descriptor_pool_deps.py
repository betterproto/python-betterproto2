"""Import-time descriptor pool ordering (betterproto2 issue #150)."""

from tests.util import requires_protobuf  # noqa: F401


def test_descriptor_options_import(requires_protobuf):
    """
    Custom options that import google/protobuf/descriptor.proto should import.

    Reproduces https://github.com/betterproto/python-betterproto2/issues/150.
    """
    from tests.outputs.descriptor_options_descriptors.descriptor_options import MyMessage

    assert MyMessage.DESCRIPTOR.full_name == "descriptor_options.MyMessage"


def test_descriptor_cross_package_import(requires_protobuf):
    """
    A package whose proto imports another package must load that package first.
    """
    from tests.outputs.descriptor_cross_package_descriptors.descriptor_cross_package.use import UseMsg

    assert UseMsg.DESCRIPTOR.full_name == "descriptor_cross_package.use.UseMsg"


def test_descriptor_same_package_import(requires_protobuf):
    """
    Files in one package must be registered in dependency order.
    """
    from tests.outputs.descriptor_same_package_descriptors.descriptor_same_package import Depends

    assert Depends.DESCRIPTOR.full_name == "descriptor_same_package.Depends"
