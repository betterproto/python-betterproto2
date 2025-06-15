"""Plugin model dataclasses.

These classes are meant to be an intermediate representation
of protobuf objects. They are used to organize the data collected during parsing.

The general intention is to create a doubly-linked tree-like structure
with the following types of references:
- Downwards references: from message -> fields, from output package -> messages
or from service -> service methods
- Upwards references: from field -> message, message -> package.
- Input/output message references: from a service method to it's corresponding
input/output messages, which may even be in another package.

There are convenience methods to allow climbing up and down this tree, for
example to retrieve the list of all messages that are in the same package as
the current message.

Most of these classes take as inputs:
- proto_obj: A reference to it's corresponding protobuf object as
presented by the protoc plugin.
- parent: a reference to the parent object in the tree.

With this information, the class is able to expose attributes,
such as a pythonized name, that will be calculated from proto_obj.
"""

import builtins
import inspect
from collections.abc import Iterator
from dataclasses import (
    dataclass,
    field,
)

from betterproto2 import unwrap

from betterproto2_compiler.compile.importing import get_symbol_reference, get_type_reference, parse_source_type_name
from betterproto2_compiler.compile.naming import (
    pythonize_class_name,
    pythonize_enum_member_name,
    pythonize_field_name,
    pythonize_method_name,
)
from betterproto2_compiler.known_types import KNOWN_METHODS, WRAPPED_TYPES
from betterproto2_compiler.lib.google.protobuf import (
    DescriptorProto,
    EnumDescriptorProto,
    FieldDescriptorProto,
    FieldDescriptorProtoLabel,
    FieldDescriptorProtoType,
    FieldDescriptorProtoType as FieldType,
    FileDescriptorProto,
    MethodDescriptorProto,
    OneofDescriptorProto,
    ServiceDescriptorProto,
)
from betterproto2_compiler.lib.google.protobuf.compiler import CodeGeneratorRequest
from betterproto2_compiler.settings import Settings

# Organize proto types into categories
PROTO_FLOAT_TYPES = (
    FieldDescriptorProtoType.TYPE_DOUBLE,  # 1
    FieldDescriptorProtoType.TYPE_FLOAT,  # 2
)
PROTO_INT_TYPES = (
    FieldDescriptorProtoType.TYPE_INT64,  # 3
    FieldDescriptorProtoType.TYPE_UINT64,  # 4
    FieldDescriptorProtoType.TYPE_INT32,  # 5
    FieldDescriptorProtoType.TYPE_FIXED64,  # 6
    FieldDescriptorProtoType.TYPE_FIXED32,  # 7
    FieldDescriptorProtoType.TYPE_UINT32,  # 13
    FieldDescriptorProtoType.TYPE_SFIXED32,  # 15
    FieldDescriptorProtoType.TYPE_SFIXED64,  # 16
    FieldDescriptorProtoType.TYPE_SINT32,  # 17
    FieldDescriptorProtoType.TYPE_SINT64,  # 18
)
PROTO_BOOL_TYPES = (FieldDescriptorProtoType.TYPE_BOOL,)  # 8
PROTO_STR_TYPES = (FieldDescriptorProtoType.TYPE_STRING,)  # 9
PROTO_BYTES_TYPES = (FieldDescriptorProtoType.TYPE_BYTES,)  # 12
PROTO_MESSAGE_TYPES = (
    FieldDescriptorProtoType.TYPE_MESSAGE,  # 11
    FieldDescriptorProtoType.TYPE_ENUM,  # 14
)
PROTO_MAP_TYPES = (FieldDescriptorProtoType.TYPE_MESSAGE,)  # 11
PROTO_PACKED_TYPES = (
    FieldDescriptorProtoType.TYPE_DOUBLE,  # 1
    FieldDescriptorProtoType.TYPE_FLOAT,  # 2
    FieldDescriptorProtoType.TYPE_INT64,  # 3
    FieldDescriptorProtoType.TYPE_UINT64,  # 4
    FieldDescriptorProtoType.TYPE_INT32,  # 5
    FieldDescriptorProtoType.TYPE_FIXED64,  # 6
    FieldDescriptorProtoType.TYPE_FIXED32,  # 7
    FieldDescriptorProtoType.TYPE_BOOL,  # 8
    FieldDescriptorProtoType.TYPE_UINT32,  # 13
    FieldDescriptorProtoType.TYPE_SFIXED32,  # 15
    FieldDescriptorProtoType.TYPE_SFIXED64,  # 16
    FieldDescriptorProtoType.TYPE_SINT32,  # 17
    FieldDescriptorProtoType.TYPE_SINT64,  # 18
)


def get_comment(
    proto_file: "FileDescriptorProto",
    path: list[int],
) -> str:
    for sci_loc in unwrap(proto_file.source_code_info).location:
        if list(sci_loc.path) == path:
            all_comments = list(sci_loc.leading_detached_comments)
            if sci_loc.leading_comments:
                all_comments.append(sci_loc.leading_comments)
            if sci_loc.trailing_comments:
                all_comments.append(sci_loc.trailing_comments)

            lines = []

            for comment in all_comments:
                lines += comment.split("\n")
                lines.append("")

            # Remove consecutive empty lines
            lines = [line for i, line in enumerate(lines) if line or (i == 0 or lines[i - 1])]

            if lines and not lines[-1]:
                lines.pop()  # Remove the last empty line

            # It is common for one line comments to start with a space, for example: // comment
            # We don't add this space to the generated file.
            lines = [line[1:] if line and line[0] == " " else line for line in lines]

            comment = "\n".join(lines)

            # Escape backslashes and triple quotes
            comment = comment.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')

            return comment

    return ""


@dataclass(kw_only=True)
class ProtoContentBase:
    """Methods common to MessageCompiler, ServiceCompiler and ServiceMethodCompiler."""

    source_file: FileDescriptorProto
    path: list[int]

    def ready(self) -> None:
        """
        This function is called after all the compilers are created, but before generating the output code.
        """
        pass

    @property
    def comment(self) -> str:
        """Crawl the proto source code and retrieve comments
        for this object.
        """
        return get_comment(proto_file=self.source_file, path=self.path)


@dataclass(kw_only=True)
class PluginRequestCompiler:
    plugin_request_obj: CodeGeneratorRequest
    output_packages: dict[str, "OutputTemplate"] = field(default_factory=dict)

    @property
    def all_messages(self) -> list["MessageCompiler"]:
        """All of the messages in this request.

        Returns
        -------
        List[MessageCompiler]
            List of all of the messages in this request.
        """
        return [msg for output in self.output_packages.values() for msg in output.messages.values()]


@dataclass(kw_only=True)
class OutputTemplate:
    """Representation of an output .py file.

    Each output file corresponds to a .proto input file,
    but may need references to other .proto files to be
    built.
    """

    parent_request: PluginRequestCompiler
    package_proto_obj: FileDescriptorProto
    input_files: list[FileDescriptorProto] = field(default_factory=list)
    imports_end: set[str] = field(default_factory=set)
    messages: dict[str, "MessageCompiler"] = field(default_factory=dict)
    enums: dict[str, "EnumDefinitionCompiler"] = field(default_factory=dict)
    services: dict[str, "ServiceCompiler"] = field(default_factory=dict)

    settings: Settings

    @property
    def package(self) -> str:
        """Name of input package.

        Returns
        -------
        str
            Name of input package.
        """
        return self.package_proto_obj.package

    @property
    def input_filenames(self) -> list[str]:
        """Names of the input files used to build this output.

        Returns
        -------
        list[str]
            Names of the input files used to build this output.
        """
        return sorted([f.name for f in self.input_files])

    @property
    def dependency_imports(self):
        """Proto dependencies as Python imports.

        Returns
        -------
        list[str]
            Imports for each proto dependency of this package resolved to the output
            names, not the input file paths.
        """
        def dep_to_pkg_import(dep: str) -> tuple[str, str]:
            for (output_name, pkg) in self.parent_request.output_packages.items():
                if dep in pkg.input_filenames:
                    ref, ref_import = get_symbol_reference(
                        package=self.package,
                        imports=self.imports_end,
                        source_package=output_name,
                        request=self.parent_request,
                        symbol="_COMPILER_VERSION",
                        import_suffx="_dep"
                    )

                    # import and check compiler version for safety and to avoid this import being removed.
                    return (ref, f'{ref_import}\nbetterproto2.check_compiler_version({ref})')
            raise ValueError(f"cannot find which output package {dep} belongs to")
        return dict([dep_to_pkg_import(dep) for dep in self.package_proto_obj.dependency]).values()

    def get_descriptor_name(self, source_file: FileDescriptorProto):
        return f'{source_file.name.replace('/', '_').replace('.', '_').upper()}_DESCRIPTOR'

    @property
    def descriptors(self):
        """Google protobuf library descriptors.

        Returns
        -------
        str
            A list of pool registrations for proto descriptors.
        """
        return '\n'.join([f'{self.get_descriptor_name(input_file)} = _descriptor_pool.Default().AddSerializedFile({input_file.SerializeToString()})' for input_file in self.input_files])

@dataclass(kw_only=True)
class MessageCompiler(ProtoContentBase):
    """Representation of a protobuf message."""

    output_file: OutputTemplate
    proto_obj: DescriptorProto
    fields: list["FieldCompiler"] = field(default_factory=list)
    oneofs: list["OneofCompiler"] = field(default_factory=list)
    builtins_types: set[str] = field(default_factory=set)

    @property
    def proto_name(self) -> str:
        return self.proto_obj.name

    @property
    def py_name(self) -> str:
        return pythonize_class_name(self.proto_name)

    @property
    def deprecated(self) -> bool:
        return bool(self.proto_obj.options and self.proto_obj.options.deprecated)

    @property
    def deprecated_fields(self) -> Iterator[str]:
        for f in self.fields:
            if f.deprecated:
                yield f.py_name

    @property
    def has_deprecated_fields(self) -> bool:
        return any(self.deprecated_fields)

    @property
    def has_oneof_fields(self) -> bool:
        return any(isinstance(field, OneOfFieldCompiler) for field in self.fields)

    @property
    def custom_methods(self) -> list[str]:
        """
        Return a list of the custom methods.
        """
        methods_source: list[str] = []

        for method in KNOWN_METHODS.get((self.source_file.package, self.py_name), []):
            source = inspect.getsource(method)
            methods_source.append(source.strip())

        return methods_source

    @property
    def descriptor_name(self):
        """Google protobuf library descriptor name.

        Returns
        -------
        str
            The Python name of the descriptor to reference.
        """
        return self.output_file.get_descriptor_name(self.source_file)

    @property
    def descriptor(self):
        """Google protobuf library descriptor.

        Returns
        -------
        str
            A binary string of the message's proto descriptor.
        """
        return self.proto_obj.SerializeToString()


def is_map(proto_field_obj: FieldDescriptorProto, parent_message: DescriptorProto) -> bool:
    """True if proto_field_obj is a map, otherwise False."""
    if proto_field_obj.type == FieldDescriptorProtoType.TYPE_MESSAGE:
        if not hasattr(parent_message, "nested_type"):
            return False

        # This might be a map...
        message_type = proto_field_obj.type_name.split(".").pop().lower()
        map_entry = f"{proto_field_obj.name.replace('_', '').lower()}entry"
        if message_type == map_entry:
            for nested in parent_message.nested_type:  # parent message
                if nested.name.replace("_", "").lower() == map_entry and nested.options and nested.options.map_entry:
                    return True
    return False


def is_oneof(proto_field_obj: FieldDescriptorProto) -> bool:
    """
    True if proto_field_obj is a OneOf, otherwise False.
    """
    return not proto_field_obj.proto3_optional and proto_field_obj.oneof_index is not None


@dataclass(kw_only=True)
class FieldCompiler(ProtoContentBase):
    builtins_types: set[str] = field(default_factory=set)

    message: MessageCompiler
    proto_obj: FieldDescriptorProto

    @property
    def output_file(self) -> "OutputTemplate":
        return self.message.output_file

    def get_field_string(self) -> str:
        """Construct string representation of this field as a field."""
        name = f"{self.py_name}"
        field_args = ", ".join(([""] + self.betterproto_field_args) if self.betterproto_field_args else [])

        betterproto_field_type = (
            f"betterproto2.field({self.proto_obj.number}, betterproto2.{str(self.field_type)}{field_args})"
        )
        if self.py_name in dir(builtins):
            self.message.builtins_types.add(self.py_name)
        return f'{name}: "{self.annotation}" = {betterproto_field_type}'

    @property
    def betterproto_field_args(self) -> list[str]:
        args = []

        if self.field_type == FieldDescriptorProtoType.TYPE_MESSAGE and self.is_wrapped:
            unwrap_type = self.unwrapped_py_type

            # Without the lambda function, the type is evaluated right away, which fails since the corresponding
            # import is placed at the end of the file to avoid circular imports.
            args.append(f"unwrap=lambda: {unwrap_type}")

        if self.optional:
            args.append("optional=True")
        elif self.repeated:
            args.append("repeated=True")
        elif self.field_type == FieldType.TYPE_ENUM:
            args.append(f"default_factory=lambda: {self.py_type}(0)")
        return args

    @property
    def deprecated(self) -> bool:
        return bool(self.proto_obj.options and self.proto_obj.options.deprecated)

    @property
    def use_builtins(self) -> bool:
        return self.py_type in self.message.builtins_types or (
            self.py_type == self.py_name and self.py_name in dir(builtins)
        )

    @property
    def repeated(self) -> bool:
        return self.proto_obj.label == FieldDescriptorProtoLabel.LABEL_REPEATED

    @property
    def optional(self) -> bool:
        # TODO not for maps
        return self.proto_obj.proto3_optional or (self.field_type == FieldType.TYPE_MESSAGE and not self.repeated)

    @property
    def field_type(self) -> FieldType:
        return self.proto_obj.type

    @property
    def packed(self) -> bool:
        """True if the wire representation is a packed format."""
        return self.repeated and self.proto_obj.type in PROTO_PACKED_TYPES

    @property
    def py_name(self) -> str:
        """Pythonized name."""
        return pythonize_field_name(self.proto_name)

    @property
    def proto_name(self) -> str:
        """Original protobuf name."""
        return self.proto_obj.name

    @property
    def is_wrapped(self) -> bool:
        assert self.field_type == FieldDescriptorProtoType.TYPE_MESSAGE
        type_package, type_name = parse_source_type_name(self.proto_obj.type_name, self.output_file.parent_request)

        return (type_package, type_name) in WRAPPED_TYPES

    def _py_type(self, wrap: bool) -> str:
        """String representation of Python type."""
        if self.proto_obj.type in PROTO_FLOAT_TYPES:
            return "float"
        elif self.proto_obj.type in PROTO_INT_TYPES:
            return "int"
        elif self.proto_obj.type in PROTO_BOOL_TYPES:
            return "bool"
        elif self.proto_obj.type in PROTO_STR_TYPES:
            return "str"
        elif self.proto_obj.type in PROTO_BYTES_TYPES:
            return "bytes"
        elif self.proto_obj.type in PROTO_MESSAGE_TYPES:
            # Type referencing another defined Message or a named enum
            return get_type_reference(
                package=self.output_file.package,
                imports=self.output_file.imports_end,
                source_type=self.proto_obj.type_name,
                request=self.output_file.parent_request,
                wrap=wrap,
                settings=self.output_file.settings,
            )
        else:
            raise NotImplementedError(f"Unknown type {self.proto_obj.type}")

    @property
    def py_type(self) -> str:
        return self._py_type(wrap=True)

    @property
    def unwrapped_py_type(self) -> str:
        return self._py_type(wrap=False)

    @property
    def annotations(self) -> list[str]:
        """List of the Pydantic annotation to add to the field."""
        assert self.output_file.settings.pydantic_dataclasses

        annotations = []

        if self.proto_obj.type in (FieldType.TYPE_INT32, FieldType.TYPE_SFIXED32, FieldType.TYPE_SINT32):
            annotations.append("pydantic.Field(ge=-2**31, le=2**31 - 1)")

        elif self.proto_obj.type in (FieldType.TYPE_UINT32, FieldType.TYPE_FIXED32):
            annotations.append("pydantic.Field(ge=0, le=2**32 - 1)")

        elif self.proto_obj.type in (FieldType.TYPE_INT64, FieldType.TYPE_SFIXED64, FieldType.TYPE_SINT64):
            annotations.append("pydantic.Field(ge=-2**63, le=2**63 - 1)")

        elif self.proto_obj.type in (FieldType.TYPE_UINT64, FieldType.TYPE_FIXED64):
            annotations.append("pydantic.Field(ge=0, le=2**64 - 1)")

        elif self.proto_obj.type == FieldType.TYPE_FLOAT:
            annotations.append("pydantic.AfterValidator(betterproto2.validators.validate_float32)")

        elif self.proto_obj.type == FieldType.TYPE_STRING:
            annotations.append("pydantic.AfterValidator(betterproto2.validators.validate_string)")

        return annotations

    @property
    def annotation(self) -> str:
        py_type = self.py_type

        if self.use_builtins:
            py_type = f"builtins.{py_type}"

        # Add the pydantic annotation if needed
        if self.output_file.settings.pydantic_dataclasses:
            annotations = self.annotations
            if annotations:
                py_type = f"typing.Annotated[{py_type}, {', '.join(annotations)}]"

        if self.repeated:
            return f"list[{py_type}]"
        if self.optional:
            return f"{py_type} | None"
        return py_type


@dataclass(kw_only=True)
class OneOfFieldCompiler(FieldCompiler):
    @property
    def optional(self) -> bool:
        return True

    @property
    def betterproto_field_args(self) -> list[str]:
        args = super().betterproto_field_args
        group = self.message.proto_obj.oneof_decl[unwrap(self.proto_obj.oneof_index)].name
        args.append(f'group="{group}"')
        return args


@dataclass(kw_only=True)
class MapEntryCompiler(FieldCompiler):
    py_k_type: str = ""
    py_v_type: str = ""
    unwrap_v: str | None = None

    proto_k_type: str = ""
    proto_v_type: str = ""

    def ready(self) -> None:
        """Explore nested types and set k_type and v_type if unset."""
        map_entry = f"{self.proto_obj.name.replace('_', '').lower()}entry"
        for nested in self.message.proto_obj.nested_type:
            if nested.name.replace("_", "").lower() == map_entry and unwrap(nested.options).map_entry:
                # Get Python types
                assert nested.field[0].name == "key"
                self.py_k_type = FieldCompiler(
                    source_file=self.source_file,
                    proto_obj=nested.field[0],  # key
                    path=[],
                    message=self.message,
                ).py_type

                assert nested.field[1].name == "value"
                value_field_compiler = FieldCompiler(
                    source_file=self.source_file,
                    proto_obj=nested.field[1],  # value
                    path=[],
                    message=self.message,
                )

                self.py_v_type = value_field_compiler.py_type
                if (
                    value_field_compiler.field_type == FieldDescriptorProtoType.TYPE_MESSAGE
                    and value_field_compiler.is_wrapped
                ):
                    self.unwrap_v = value_field_compiler.unwrapped_py_type
                else:
                    self.unwrap_v = None

                # Get proto types
                self.proto_k_type = unwrap(FieldDescriptorProtoType(nested.field[0].type).name)
                self.proto_v_type = unwrap(FieldDescriptorProtoType(nested.field[1].type).name)
                return

        raise ValueError("can't find enum")

    def get_field_string(self) -> str:
        """Construct string representation of this field as a field."""
        proto_type_1 = f"betterproto2.{self.proto_k_type}"
        proto_type_2 = f"betterproto2.{self.proto_v_type}"

        unwrap_2 = ""
        if self.unwrap_v:
            unwrap_2 = f", unwrap_2=lambda: {self.unwrap_v}"

        betterproto_field_type = (
            "betterproto2.field("
            f"{self.proto_obj.number}, "
            "betterproto2.TYPE_MAP, "
            f"map_meta=betterproto2.map_meta({proto_type_1}, {proto_type_2}{unwrap_2})"
            ")"
        )
        if self.py_name in dir(builtins):
            self.message.builtins_types.add(self.py_name)
        return f'{self.py_name}: "{self.annotation}" = {betterproto_field_type}'

    @property
    def annotation(self) -> str:
        return f"dict[{self.py_k_type}, {self.py_v_type}]"

    @property
    def repeated(self) -> bool:
        return False  # maps cannot be repeated


@dataclass(kw_only=True)
class OneofCompiler(ProtoContentBase):
    proto_obj: OneofDescriptorProto

    @property
    def name(self) -> str:
        return self.proto_obj.name


@dataclass(kw_only=True)
class EnumDefinitionCompiler(ProtoContentBase):
    """Representation of a proto Enum definition."""

    output_file: OutputTemplate
    proto_obj: EnumDescriptorProto
    entries: list["EnumDefinitionCompiler.EnumEntry"] = field(default_factory=list)

    @dataclass(unsafe_hash=True, kw_only=True)
    class EnumEntry:
        """Representation of an Enum entry."""

        name: str
        value: int
        comment: str

    def __post_init__(self) -> None:
        # Get entries/allowed values for this Enum
        self.entries = [
            self.EnumEntry(
                name=pythonize_enum_member_name(entry_proto_value.name, self.proto_obj.name),
                value=entry_proto_value.number,
                comment=get_comment(proto_file=self.source_file, path=self.path + [2, entry_number]),
            )
            for entry_number, entry_proto_value in enumerate(self.proto_obj.value)
        ]

    @property
    def proto_name(self) -> str:
        return self.proto_obj.name

    @property
    def py_name(self) -> str:
        return pythonize_class_name(self.proto_name)

    @property
    def deprecated(self) -> bool:
        return bool(self.proto_obj.options and self.proto_obj.options.deprecated)

    @property
    def descriptor_name(self):
        """Google protobuf library descriptor name.

        Returns
        -------
        str
            The Python name of the descriptor to reference.
        """
        return self.output_file.get_descriptor_name(self.source_file)

    @property
    def descriptor(self):
        """Google protobuf library descriptor.

        Returns
        -------
        str
            A binary string of the enum's proto descriptor.
        """
        return self.proto_obj.SerializeToString()


@dataclass(kw_only=True)
class ServiceCompiler(ProtoContentBase):
    output_file: OutputTemplate
    proto_obj: ServiceDescriptorProto
    methods: list["ServiceMethodCompiler"] = field(default_factory=list)

    @property
    def proto_name(self) -> str:
        return self.proto_obj.name

    @property
    def py_name(self) -> str:
        return pythonize_class_name(self.proto_name)


@dataclass(kw_only=True)
class ServiceMethodCompiler(ProtoContentBase):
    parent: ServiceCompiler
    proto_obj: MethodDescriptorProto

    @property
    def py_name(self) -> str:
        """Pythonized method name."""
        return pythonize_method_name(self.proto_obj.name)

    @property
    def proto_name(self) -> str:
        """Original protobuf name."""
        return self.proto_obj.name

    @property
    def route(self) -> str:
        package_part = f"{self.parent.output_file.package}." if self.parent.output_file.package else ""
        return f"/{package_part}{self.parent.proto_name}/{self.proto_name}"

    @property
    def py_input_message_type(self) -> str:
        """String representation of the Python type corresponding to the
        input message.

        Returns
        -------
        str
            String representation of the Python type corresponding to the input message.
        """
        return get_type_reference(
            package=self.parent.output_file.package,
            imports=self.parent.output_file.imports_end,
            source_type=self.proto_obj.input_type,
            request=self.parent.output_file.parent_request,
            wrap=False,
            settings=self.parent.output_file.settings,
        )

    @property
    def is_input_msg_empty(self: "ServiceMethodCompiler") -> bool:
        package, name = parse_source_type_name(self.proto_obj.input_type, self.parent.output_file.parent_request)

        msg = self.parent.output_file.parent_request.output_packages[package].messages[name]

        return not bool(msg.fields)

    @property
    def py_output_message_type(self) -> str:
        """String representation of the Python type corresponding to the
        output message.

        Returns
        -------
        str
            String representation of the Python type corresponding to the output message.
        """
        return get_type_reference(
            package=self.parent.output_file.package,
            imports=self.parent.output_file.imports_end,
            source_type=self.proto_obj.output_type,
            request=self.parent.output_file.parent_request,
            wrap=False,
            settings=self.parent.output_file.settings,
        )

    @property
    def client_streaming(self) -> bool:
        return self.proto_obj.client_streaming

    @property
    def server_streaming(self) -> bool:
        return self.proto_obj.server_streaming

    @property
    def deprecated(self) -> bool:
        return bool(self.proto_obj.options and self.proto_obj.options.deprecated)
