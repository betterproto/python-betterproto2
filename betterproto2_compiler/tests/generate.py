#!/usr/bin/env python
import asyncio
import os
import shutil

from tests.util import (
    # TODO delete definitions?
    # get_directories,
    # inputs_path,
    # output_path_betterproto,
    # output_path_betterproto_descriptor,
    # output_path_betterproto_pydantic,
    # output_path_reference,
    protoc,
)

# Force pure-python implementation instead of C++, otherwise imports
# break things because we can't properly reset the symbol database.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


# async def generate(verbose: bool):
#     failed_test_cases = []
#     # Wait for all subprocs and match any failures to names to report
#     for test_case_name, result in zip(sorted(test_case_names), await asyncio.gather(*generation_tasks)):
#         if result != 0:
#             failed_test_cases.append(test_case_name)

#     if len(failed_test_cases) > 0:
#         sys.stderr.write("\n\033[31;1;4mFailed to generate the following test cases:\033[0m\n")
#         for failed_test_case in failed_test_cases:
#             sys.stderr.write(f"- {failed_test_case}\n")

#         sys.exit(1)


async def generate_test(
    name,
    semaphore: asyncio.Semaphore,
    *,
    reference: bool = False,
    pydantic: bool = False,
    descriptors: bool = False,
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
    output_dir = dir_path + "/outputs/" + name + ("_" + "_".join(options) if options else "")

    os.mkdir(output_dir)

    stdout, stderr, returncode = await protoc(
        input_dir,
        output_dir,
        reference=reference,
        pydantic_dataclasses=pydantic,
        google_protobuf_descriptors=descriptors,
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


async def main_async():
    # Don't compile too many tests in parallel
    semaphore = asyncio.Semaphore(4)

    tasks = [
        generate_test("any", semaphore),
        generate_test("bool", semaphore),
        generate_test("deprecated", semaphore),
        generate_test("enum", semaphore),
        generate_test("features", semaphore),
        generate_test("google", semaphore),
        generate_test("map", semaphore),
        generate_test("mapmessage", semaphore),
        generate_test("nested", semaphore),
        generate_test("oneof", semaphore),
        generate_test("pickling", semaphore),
        generate_test("recursivemessage", semaphore),
        generate_test("repeated", semaphore),
        generate_test("repeatedpacked", semaphore),
        generate_test("service", semaphore),
        generate_test("simple_service", semaphore),
    ]
    await asyncio.gather(*tasks)


def main():
    # Clean the output directory
    dir_path = os.path.dirname(os.path.realpath(__file__))

    shutil.rmtree(dir_path + "/outputs", ignore_errors=True)
    os.mkdir(dir_path + "/outputs")

    asyncio.run(main_async())


if __name__ == "__main__":
    main()
