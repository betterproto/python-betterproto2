#!/usr/bin/env python
import asyncio
import os
import shutil

from tests.util import protoc

# Force pure-python implementation instead of C++, otherwise imports
# break things because we can't properly reset the symbol database.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


async def generate_test(
    name,
    semaphore: asyncio.Semaphore,
    outputs_dir: str,
    *,
    reference: bool = False,
    pydantic: bool = False,
    descriptors: bool = False,
    client_generation: str = "async_sync",
):
    await semaphore.acquire()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    options = []
    if reference:
        options.append("reference")
    if pydantic:
        options.append("pydantic")
    if descriptors:
        options.append("descriptors")

    input_dir = dir_path + "/inputs/" + name
    output_dir = outputs_dir + "/" + name + ("_" + "_".join(options) if options else "")

    os.mkdir(output_dir)

    stdout, stderr, returncode = await protoc(
        input_dir,
        output_dir,
        reference=reference,
        pydantic_dataclasses=pydantic,
        google_protobuf_descriptors=descriptors,
        client_generation=client_generation,
    )

    if options:
        options_str = ", ".join(options)
        options_str = f" ({options_str})"
    else:
        options_str = ""

    if returncode == 0:
        print(f"\033[31;1;4mGenerated output for {name!r}{options_str}\033[0m")
    else:
        print(f"\033[31;1;4mFailed to generate reference output for {name!r}{options_str}\033[0m")
        print(stderr.decode())

    semaphore.release()


async def main_async(outputs_dir: str):
    # Don't compile too many tests in parallel
    semaphore = asyncio.Semaphore(os.cpu_count() or 1)

    tasks = [
        generate_test("any", semaphore, outputs_dir),
        generate_test("bool", semaphore, outputs_dir, pydantic=True),
        generate_test("bool", semaphore, outputs_dir, reference=True),
        generate_test("bool", semaphore, outputs_dir),
        generate_test("bytes", semaphore, outputs_dir, reference=True),
        generate_test("bytes", semaphore, outputs_dir),
        generate_test("casing_inner_class", semaphore, outputs_dir),
        generate_test("casing", semaphore, outputs_dir, reference=True),
        generate_test("casing", semaphore, outputs_dir),
        generate_test("compiler_lib", semaphore, outputs_dir),
        generate_test("conformance", semaphore, outputs_dir),
        generate_test("descriptor_cross_package", semaphore, outputs_dir, descriptors=True),
        generate_test("descriptor_options", semaphore, outputs_dir, descriptors=True),
        generate_test("descriptor_same_package", semaphore, outputs_dir, descriptors=True),
        generate_test("deprecated", semaphore, outputs_dir, reference=True),
        generate_test("deprecated", semaphore, outputs_dir, client_generation="async"),
        generate_test("documentation", semaphore, outputs_dir, client_generation="async"),
        generate_test("double", semaphore, outputs_dir, reference=True),
        generate_test("double", semaphore, outputs_dir),
        generate_test("encoding_decoding", semaphore, outputs_dir),
        generate_test("enum", semaphore, outputs_dir, reference=True),
        generate_test("enum", semaphore, outputs_dir),
        generate_test("example_service", semaphore, outputs_dir, client_generation="async"),
        generate_test("features", semaphore, outputs_dir),
        generate_test("field_name_identical_to_type", semaphore, outputs_dir, reference=True),
        generate_test("field_name_identical_to_type", semaphore, outputs_dir),
        generate_test("fixed", semaphore, outputs_dir, reference=True),
        generate_test("fixed", semaphore, outputs_dir),
        generate_test("float", semaphore, outputs_dir, reference=True),
        generate_test("float", semaphore, outputs_dir),
        generate_test("google_impl_behavior_equivalence", semaphore, outputs_dir, reference=True),
        generate_test("google_impl_behavior_equivalence", semaphore, outputs_dir),
        generate_test("google", semaphore, outputs_dir),
        generate_test("googletypes_request", semaphore, outputs_dir, client_generation="async"),
        generate_test("googletypes_response_embedded", semaphore, outputs_dir, client_generation="async"),
        generate_test("googletypes_response", semaphore, outputs_dir, client_generation="async"),
        generate_test("googletypes_struct", semaphore, outputs_dir, reference=True),
        generate_test("googletypes_struct", semaphore, outputs_dir),
        generate_test("googletypes_value", semaphore, outputs_dir, reference=True),
        generate_test("googletypes_value", semaphore, outputs_dir),
        generate_test("googletypes", semaphore, outputs_dir, reference=True),
        generate_test("googletypes", semaphore, outputs_dir),
        generate_test("grpclib_reflection", semaphore, outputs_dir, descriptors=True, client_generation="async"),
        generate_test("grpclib_reflection", semaphore, outputs_dir, client_generation="async"),
        generate_test("import_cousin_package_same_name", semaphore, outputs_dir, descriptors=True),
        generate_test("import_cousin_package_same_name", semaphore, outputs_dir),
        generate_test("import_service_input_message", semaphore, outputs_dir, client_generation="async"),
        generate_test("int32", semaphore, outputs_dir, reference=True),
        generate_test("int32", semaphore, outputs_dir),
        generate_test("invalid_field", semaphore, outputs_dir, pydantic=True),
        generate_test("invalid_field", semaphore, outputs_dir),
        generate_test("manual_validation", semaphore, outputs_dir, pydantic=True),
        generate_test("manual_validation", semaphore, outputs_dir),
        generate_test("map", semaphore, outputs_dir, reference=True),
        generate_test("map", semaphore, outputs_dir),
        generate_test("mapmessage", semaphore, outputs_dir, reference=True),
        generate_test("mapmessage", semaphore, outputs_dir),
        generate_test("message_wrapping", semaphore, outputs_dir),
        generate_test("namespace_builtin_types", semaphore, outputs_dir, reference=True),
        generate_test("namespace_builtin_types", semaphore, outputs_dir),
        generate_test("namespace_keywords", semaphore, outputs_dir, reference=True),
        generate_test("namespace_keywords", semaphore, outputs_dir),
        generate_test("nested", semaphore, outputs_dir, reference=True),
        generate_test("nested", semaphore, outputs_dir),
        generate_test("nestedtwice", semaphore, outputs_dir, reference=True),
        generate_test("nestedtwice", semaphore, outputs_dir),
        generate_test("oneof_default_value_serialization", semaphore, outputs_dir),
        generate_test("oneof_empty", semaphore, outputs_dir, reference=True),
        generate_test("oneof_empty", semaphore, outputs_dir),
        generate_test("oneof_enum", semaphore, outputs_dir, reference=True),
        generate_test("oneof_enum", semaphore, outputs_dir),
        generate_test("oneof", semaphore, outputs_dir, pydantic=True),
        generate_test("oneof", semaphore, outputs_dir, reference=True),
        generate_test("oneof", semaphore, outputs_dir),
        generate_test("pickling", semaphore, outputs_dir),
        generate_test("proto3_field_presence_oneof", semaphore, outputs_dir, reference=True),
        generate_test("proto3_field_presence_oneof", semaphore, outputs_dir),
        generate_test("proto3_field_presence", semaphore, outputs_dir, reference=True),
        generate_test("proto3_field_presence", semaphore, outputs_dir),
        generate_test("recursivemessage", semaphore, outputs_dir, reference=True),
        generate_test("recursivemessage", semaphore, outputs_dir),
        generate_test("ref", semaphore, outputs_dir, reference=True),
        generate_test("ref", semaphore, outputs_dir),
        generate_test("regression_387", semaphore, outputs_dir),
        generate_test("regression_414", semaphore, outputs_dir),
        generate_test("repeated_duration_timestamp", semaphore, outputs_dir, reference=True),
        generate_test("repeated_duration_timestamp", semaphore, outputs_dir),
        generate_test("repeated", semaphore, outputs_dir, reference=True),
        generate_test("repeated", semaphore, outputs_dir),
        generate_test("repeatedmessage", semaphore, outputs_dir, reference=True),
        generate_test("repeatedmessage", semaphore, outputs_dir),
        generate_test("repeatedpacked", semaphore, outputs_dir, reference=True),
        generate_test("repeatedpacked", semaphore, outputs_dir),
        generate_test("rpc_empty_input_message", semaphore, outputs_dir, client_generation="async"),
        generate_test("service_uppercase", semaphore, outputs_dir, client_generation="async"),
        generate_test("service", semaphore, outputs_dir),
        generate_test("signed", semaphore, outputs_dir, reference=True),
        generate_test("signed", semaphore, outputs_dir),
        generate_test("simple_service", semaphore, outputs_dir),
        generate_test("stream_stream", semaphore, outputs_dir),
        generate_test("timestamp_dict_encode", semaphore, outputs_dir, reference=True),
        generate_test("timestamp_dict_encode", semaphore, outputs_dir),
        generate_test("unwrap", semaphore, outputs_dir),
        generate_test("validation", semaphore, outputs_dir, pydantic=True),
    ]
    await asyncio.gather(*tasks)


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    outputs_dir = os.path.normpath(os.path.join(dir_path, "../../betterproto2/tests/outputs"))

    shutil.rmtree(outputs_dir, ignore_errors=True)
    os.mkdir(outputs_dir)

    asyncio.run(main_async(outputs_dir))


if __name__ == "__main__":
    main()
