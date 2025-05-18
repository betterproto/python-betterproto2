from importlib import metadata

__version__ = metadata.version("betterproto2")


def check_compiler_version(compiler_version: str) -> None:
    """
    Checks that the compiled files can be used with this version of the library.

    If the versions do not match, the user is suggested to update the library or the compiler. The version x.y.z of the
    library matches the version a.b.c of the compiler if and only if a=x and b=y.
    """
    parsed_lib_version = tuple(int(x) for x in __version__.split(".")[:2])
    parsed_comp_version = tuple(int(x) for x in compiler_version.split(".")[:2])

    if parsed_lib_version != parsed_comp_version:
        error = (
            f"Unsupported version. The proto files were compiled with a version of betterproto2_compiler which is not "
            "compatible with this version of betterproto2.\n"
            f" - betterproto2 version: {__version__}\n"
            f" - betterproto2_compiler version: {compiler_version}\n"
            "The version x.y.z of the library matches the version a.b.c of the compiler if and only if a=x and b=y.\n"
        )

        if parsed_lib_version < parsed_comp_version:
            error += (
                f"Please upgrade betterproto2 to {parsed_comp_version[0]}.{parsed_comp_version[1]}.x (recommended) "
                f"or downgrade betterproto2_compiler to {parsed_lib_version[0]}.{parsed_lib_version[1]}.x and "
                "recompile your proto files."
            )
        else:
            error += (
                f"Please upgrade betterproto2_compiler to {parsed_lib_version[0]}.{parsed_lib_version[1]}.x and "
                "recompile your proto files (recommended) or downgrade betterproto2 to "
                f"{parsed_comp_version[0]}.{parsed_comp_version[1]}.x."
            )

        raise ImportError(error)
