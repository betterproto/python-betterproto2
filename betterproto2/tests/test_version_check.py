import pytest


def test_check_compiler_version():
    from betterproto2 import __version__, check_compiler_version

    x, y, z = (int(x) for x in __version__.split("."))

    check_compiler_version(__version__)
    check_compiler_version(f"{x}.{y}.{z - 1}")
    check_compiler_version(f"{x}.{y}.{z + 1}")

    with pytest.raises(ImportError):
        check_compiler_version(f"{x}.{y - 1}.{z}")

    with pytest.raises(ImportError):
        check_compiler_version(f"{x}.{y + 1}.{z}")

    with pytest.raises(ImportError):
        check_compiler_version(f"{x + 1}.{y}.{z}")

    with pytest.raises(ImportError):
        check_compiler_version(f"{x - 1}.{y}.{z}")
