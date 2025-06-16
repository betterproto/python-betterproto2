from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
)

from betterproto2_compiler.known_types import WRAPPED_TYPES
from betterproto2_compiler.settings import Settings

from ..casing import safe_snake_case
from .naming import pythonize_class_name

if TYPE_CHECKING:
    from ..plugin.models import PluginRequestCompiler


def parse_source_type_name(field_type_name: str, request: PluginRequestCompiler) -> tuple[str, str]:
    """
    Split full source type name into package and type name.
    E.g. 'root.package.Message' -> ('root.package', 'Message')
         'root.Message.SomeEnum' -> ('root', 'Message.SomeEnum')

    The function goes through the symbols that have been defined (names, enums,
    packages) to find the actual package and name of the object that is referenced.
    """
    if field_type_name[0] != ".":
        raise RuntimeError("relative names are not supported")
    field_type_name = field_type_name[1:]
    parts = field_type_name.split(".")

    answer = None

    # a.b.c:
    # i=0: "", "a.b.c"
    # i=1: "a", "b.c"
    # i=2: "a.b", "c"
    for i in range(len(parts)):
        package_name, object_name = ".".join(parts[:i]), ".".join(parts[i:])

        package = request.output_packages.get(package_name)

        if not package:
            continue

        if object_name in package.messages or object_name in package.enums:
            if answer:
                # This should have already been handeled by protoc
                raise ValueError(f"ambiguous definition: {field_type_name}")
            answer = package_name, object_name

    if answer:
        return answer

    raise ValueError(f"can't find type name: {field_type_name}")


def get_symbol_reference(
    *,
    package: str,
    imports: set,
    source_package: str,
    symbol: str,
    request: PluginRequestCompiler,
    import_suffx: str = "",
) -> tuple[str, str | None]:
    """
    Return a Python symbol within a proto package. Adds the import if
    necessary and returns it as well for usage. Unwraps well known type if required.
    """
    current_package: list[str] = package.split(".") if package else []
    py_package: list[str] = source_package.split(".") if source_package else []

    if py_package == current_package:
        return (reference_sibling(symbol), None)

    if py_package[: len(current_package)] == current_package:
        return reference_descendent(current_package, imports, py_package, symbol, import_suffx)

    if current_package[: len(py_package)] == py_package:
        return reference_ancestor(current_package, imports, py_package, symbol, import_suffx)

    return reference_cousin(current_package, imports, py_package, symbol, import_suffx)


def get_type_reference(
    *,
    package: str,
    imports: set,
    source_type: str,
    request: PluginRequestCompiler,
    wrap: bool = True,
    settings: Settings,
) -> str:
    """
    Return a Python type name for a proto type reference. Adds the import if
    necessary. Unwraps well known type if required.
    """
    source_package, source_type = parse_source_type_name(source_type, request)

    if wrap and (source_package, source_type) in WRAPPED_TYPES:
        return WRAPPED_TYPES[(source_package, source_type)]

    py_type: str = pythonize_class_name(source_type)
    (ref, _) = get_symbol_reference(
        package=package,
        imports=imports,
        source_package=source_package,
        symbol=py_type,
        request=request,
    )
    return ref


def reference_absolute(imports: set[str], py_package: list[str], py_type: str) -> tuple[str, str]:
    """
    Returns a reference to a python type located in the root, i.e. sys.path.
    """
    string_import = ".".join(py_package)
    string_alias = "__".join([safe_snake_case(name) for name in py_package])
    import_to_add = f"import {string_import} as {string_alias}"
    imports.add(import_to_add)
    return (f"{string_alias}.{py_type}", import_to_add)


def reference_sibling(py_type: str) -> str:
    """
    Returns a reference to a python type within the same package as the current package.
    """
    return f"{py_type}"


def reference_descendent(
    current_package: list[str], imports: set[str], py_package: list[str], py_type: str, import_suffix: str = ""
) -> tuple[str, str]:
    """
    Returns a reference to a python type in a package that is a descendent of the
    current package, and adds the required import that is aliased to avoid name
    conflicts.
    """
    importing_descendent = py_package[len(current_package) :]
    string_from = ".".join(importing_descendent[:-1])
    string_import = importing_descendent[-1]
    if string_from:
        string_alias = f"{'_'.join(importing_descendent)}{import_suffix}"
        import_to_add = f"from .{string_from} import {string_import} as {string_alias}"
        imports.add(import_to_add)
        return (f"{string_alias}.{py_type}", import_to_add)
    else:
        import_to_add = f"from . import {string_import}"
        imports.add(import_to_add)
        return (f"{string_import}.{py_type}", import_to_add)


def reference_ancestor(
    current_package: list[str], imports: set[str], py_package: list[str], py_type: str, import_suffix: str = ""
) -> tuple[str, str]:
    """
    Returns a reference to a python type in a package which is an ancestor to the
    current package, and adds the required import that is aliased (if possible) to avoid
    name conflicts.

    Adds trailing __ to avoid name mangling (python.org/dev/peps/pep-0008/#id34).
    """
    distance_up = len(current_package) - len(py_package)
    if py_package:
        string_import = py_package[-1]
        string_alias = f"_{'_' * distance_up}{string_import}__{import_suffix}"
        string_from = f"..{'.' * distance_up}"
        import_to_add = f"from {string_from} import {string_import} as {string_alias}"
        imports.add(import_to_add)
        return (f"{string_alias}.{py_type}", import_to_add)
    else:
        string_alias = f"{'_' * distance_up}{py_type}__{import_suffix}"
        import_to_add = f"from .{'.' * distance_up} import {py_type} as {string_alias}"
        imports.add(import_to_add)
        return (string_alias, import_to_add)


def reference_cousin(
    current_package: list[str], imports: set[str], py_package: list[str], py_type: str, import_suffix: str = ""
) -> tuple[str, str]:
    """
    Returns a reference to a python type in a package that is not descendent, ancestor
    or sibling, and adds the required import that is aliased to avoid name conflicts.
    """
    shared_ancestry = os.path.commonprefix([current_package, py_package])  # type: ignore
    distance_up = len(current_package) - len(shared_ancestry)
    string_from = f".{'.' * distance_up}" + ".".join(py_package[len(shared_ancestry) : -1])
    string_import = py_package[-1]
    # Add trailing __ to avoid name mangling (python.org/dev/peps/pep-0008/#id34)
    # string_alias = f"{'_' * distance_up}" + safe_snake_case(".".join(py_package[len(shared_ancestry) :])) + "__"
    string_alias = (
        f"{'_' * distance_up}"
        + "__".join([safe_snake_case(name) for name in py_package[len(shared_ancestry) :]])
        + "__"
        + import_suffix
    )
    import_to_add = f"from {string_from} import {string_import} as {string_alias}"
    imports.add(import_to_add)
    return (f"{string_alias}.{py_type}", import_to_add)
