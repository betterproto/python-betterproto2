import pathlib
import sys
from collections.abc import Generator

from betterproto2_compiler.lib.google.protobuf import (
    DescriptorProto,
    EnumDescriptorProto,
    FileDescriptorProto,
    ServiceDescriptorProto,
)
from betterproto2_compiler.lib.google.protobuf.compiler import (
    CodeGeneratorRequest,
    CodeGeneratorResponse,
    CodeGeneratorResponseFeature,
    CodeGeneratorResponseFile,
)
from betterproto2_compiler.settings import ClientGeneration, ServerGeneration, Settings

from .compiler import outputfile_compiler
from .models import (
    EnumDefinitionCompiler,
    FieldCompiler,
    MapEntryCompiler,
    MessageCompiler,
    OneofCompiler,
    OneOfFieldCompiler,
    OutputTemplate,
    PluginRequestCompiler,
    ServiceCompiler,
    ServiceMethodCompiler,
    is_map,
    is_oneof,
)


def traverse(
    proto_file: FileDescriptorProto,
) -> Generator[tuple[EnumDescriptorProto | DescriptorProto, list[int], str], None, None]:
    # Todo: Keep information about nested hierarchy
    def _traverse(
        path: list[int],
        items: list[EnumDescriptorProto] | list[DescriptorProto],
        prefix: str = "",
    ) -> Generator[tuple[EnumDescriptorProto | DescriptorProto, list[int], str], None, None]:
        for i, item in enumerate(items):
            # Adjust the name since we flatten the hierarchy.
            should_rename = not isinstance(item, DescriptorProto) or not item.options or not item.options.map_entry

            # Record prefixed name but *do not* mutate original file.
            # We use this prefixed name to create pythonized names.
            prefixed_name = next_prefix = f"{prefix}.{item.name}" if prefix and should_rename else item.name
            yield item, [*path, i], prefixed_name

            if isinstance(item, DescriptorProto):
                # Get nested types.
                yield from _traverse([*path, i, 4], item.enum_type, next_prefix)
                yield from _traverse([*path, i, 3], item.nested_type, next_prefix)

    yield from _traverse([5], proto_file.enum_type)
    yield from _traverse([4], proto_file.message_type)


def get_settings(plugin_options: list[str]) -> Settings:
    # Synchronous clients are suitable for most users
    client_generation = ClientGeneration.SYNC
    server_generation = ServerGeneration.NONE

    for opt in plugin_options:
        if opt.startswith("client_generation="):
            name = opt.split("=")[1]
            try:
                client_generation = ClientGeneration(name)
            except ValueError:
                raise ValueError(f"Invalid client_generation option: {name}")

        if opt.startswith("server_generation="):
            name = opt.split("=")[1]
            try:
                server_generation = ServerGeneration(name)
            except ValueError:
                raise ValueError(f"Invalid server_generation option: {name}")

    return Settings(
        pydantic_dataclasses="pydantic_dataclasses" in plugin_options,
        google_protobuf_descriptors="google_protobuf_descriptors" in plugin_options,
        client_generation=client_generation,
        server_generation=server_generation,
    )


def generate_code(request: CodeGeneratorRequest) -> CodeGeneratorResponse:
    response = CodeGeneratorResponse(supported_features=CodeGeneratorResponseFeature.PROTO3_OPTIONAL)

    plugin_options = request.parameter.split(",") if request.parameter else []
    settings = get_settings(plugin_options)

    request_data = PluginRequestCompiler(plugin_request_obj=request)
    # Gather output packages
    for proto_file in request.proto_file:
        output_package_name = proto_file.package
        if output_package_name not in request_data.output_packages:
            # Create a new output if there is no output for this package
            request_data.output_packages[output_package_name] = OutputTemplate(
                parent_request=request_data, package_proto_obj=proto_file, settings=settings
            )
        # Add this input file to the output corresponding to this package
        request_data.output_packages[output_package_name].input_files.append(proto_file)

    # Read Messages and Enums
    # We need to read Messages before Services in so that we can
    # get the references to input/output messages for each service
    for output_package_name, output_package in request_data.output_packages.items():
        for proto_input_file in output_package.input_files:
            for item, path, prefixed_proto_name in traverse(proto_input_file):
                read_protobuf_type(
                    source_file=proto_input_file,
                    item=item,
                    path=path,
                    output_package=output_package,
                    prefixed_proto_name=prefixed_proto_name,
                )

    # Read Services
    for output_package_name, output_package in request_data.output_packages.items():
        for proto_input_file in output_package.input_files:
            for index, service in enumerate(proto_input_file.service):
                read_protobuf_service(proto_input_file, service, index, output_package)

    # All the hierarchy is ready. We can perform pre-computations before generating the output files
    for package in request_data.output_packages.values():
        for message in package.messages.values():
            for field in message.fields:
                field.ready()
            message.ready()
        for enum in package.enums.values():
            enum.ready()
        for service in package.services.values():
            for method in service.methods:
                method.ready()
            service.ready()

    # Generate output files
    output_paths: set[pathlib.Path] = set()
    for output_package_name, output_package in request_data.output_packages.items():
        # Add files to the response object
        output_path = pathlib.Path(*output_package_name.split("."), "__init__.py")
        output_paths.add(output_path)

        response.file.append(
            CodeGeneratorResponseFile(
                name=str(output_path),
                # Render and then format the output file
                content=outputfile_compiler(output_file=output_package),
            ),
        )

    # Make each output directory a package with __init__ file
    init_files = {
        directory.joinpath("__init__.py")
        for path in output_paths
        for directory in path.parents
        if not directory.joinpath("__init__.py").exists()
    } - output_paths

    for init_file in init_files:
        response.file.append(CodeGeneratorResponseFile(name=str(init_file)))

    response.file.append(
        CodeGeneratorResponseFile(
            name="message_pool.py", content="import betterproto2\n\ndefault_message_pool = betterproto2.MessagePool()\n"
        )
    )

    response.file.append(CodeGeneratorResponseFile(name="py.typed", content=""))

    if settings.google_protobuf_descriptors:
        response.file.append(
            CodeGeneratorResponseFile(
                name="google_proto_descriptor_pool.py",
                content="from google.protobuf import descriptor_pool\n\n"
                + "default_google_proto_descriptor_pool = descriptor_pool.DescriptorPool()\n",
            )
        )

    for output_package_name in sorted(output_paths.union(init_files)):
        print(f"Writing {output_package_name}", file=sys.stderr)

    return response


def read_protobuf_type(
    item: DescriptorProto | EnumDescriptorProto,
    path: list[int],
    source_file: "FileDescriptorProto",
    output_package: OutputTemplate,
    prefixed_proto_name: str,
) -> None:
    if isinstance(item, DescriptorProto):
        if item.options and item.options.map_entry:
            # Skip generated map entry messages since we just use dicts
            return
        # Process Message
        message_data = MessageCompiler(
            source_file=source_file,
            output_file=output_package,
            prefixed_proto_name=prefixed_proto_name,
            proto_obj=item,
            path=path,
        )
        output_package.messages[message_data.prefixed_proto_name] = message_data

        for index, field in enumerate(item.field):
            if is_map(field, item):
                message_data.fields.append(
                    MapEntryCompiler(
                        source_file=source_file,
                        message=message_data,
                        proto_obj=field,
                        path=path + [2, index],
                    )
                )
            elif is_oneof(field):
                message_data.fields.append(
                    OneOfFieldCompiler(
                        source_file=source_file,
                        message=message_data,
                        proto_obj=field,
                        path=path + [2, index],
                    )
                )
            else:
                message_data.fields.append(
                    FieldCompiler(
                        source_file=source_file,
                        message=message_data,
                        proto_obj=field,
                        path=path + [2, index],
                    )
                )

        # Synthetic oneofs are generated for optional fields. We should not generate code or documentation for them.
        is_synthetic_oneof = [True for _ in item.oneof_decl]
        for field in item.field:
            if field.oneof_index is not None and not field.proto3_optional:
                is_synthetic_oneof[field.oneof_index] = False

        for index, (oneof, is_synthetic) in enumerate(zip(item.oneof_decl, is_synthetic_oneof)):
            if not is_synthetic:
                message_data.oneofs.append(
                    OneofCompiler(
                        source_file=source_file,
                        path=path + [8, index],
                        proto_obj=oneof,
                    )
                )

    elif isinstance(item, EnumDescriptorProto):
        # Enum
        enum = EnumDefinitionCompiler(
            source_file=source_file,
            output_file=output_package,
            prefixed_proto_name=prefixed_proto_name,
            proto_obj=item,
            path=path,
        )
        output_package.enums[enum.prefixed_proto_name] = enum


def read_protobuf_service(
    source_file: FileDescriptorProto,
    service: ServiceDescriptorProto,
    index: int,
    output_package: OutputTemplate,
) -> None:
    service_data = ServiceCompiler(
        source_file=source_file,
        output_file=output_package,
        proto_obj=service,
        path=[6, index],
    )
    service_data.output_file.services[service_data.proto_name] = service_data

    for j, method in enumerate(service.method):
        service_data.methods.append(
            ServiceMethodCompiler(
                source_file=source_file,
                parent=service_data,
                proto_obj=method,
                path=[6, index, 2, j],
            )
        )
