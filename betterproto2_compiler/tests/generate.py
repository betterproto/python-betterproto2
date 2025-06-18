#!/usr/bin/env python
import asyncio
import os
import shutil
import sys
from pathlib import Path

from tests.util import (
    get_directories,
    inputs_path,
    output_path_betterproto,
    output_path_betterproto_descriptor,
    output_path_betterproto_pydantic,
    output_path_reference,
    protoc,
)

# Force pure-python implementation instead of C++, otherwise imports
# break things because we can't properly reset the symbol database.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


def clear_directory(dir_path: Path):
    for file_or_directory in dir_path.glob("*"):
        if file_or_directory.is_dir():
            shutil.rmtree(file_or_directory)
        else:
            file_or_directory.unlink()


async def generate(verbose: bool):
    test_case_names = set(get_directories(inputs_path)) - {"__pycache__"}

    generation_tasks = []
    for test_case_name in sorted(test_case_names):
        test_case_input_path = inputs_path.joinpath(test_case_name).resolve()
        generation_tasks.append(generate_test_case_output(test_case_input_path, test_case_name, verbose))

    failed_test_cases = []
    # Wait for all subprocs and match any failures to names to report
    for test_case_name, result in zip(sorted(test_case_names), await asyncio.gather(*generation_tasks)):
        if result != 0:
            failed_test_cases.append(test_case_name)

    if len(failed_test_cases) > 0:
        sys.stderr.write("\n\033[31;1;4mFailed to generate the following test cases:\033[0m\n")
        for failed_test_case in failed_test_cases:
            sys.stderr.write(f"- {failed_test_case}\n")

        sys.exit(1)


async def generate_test_case_output(test_case_input_path: Path, test_case_name: str, verbose: bool) -> int:
    """
    Returns the max of the subprocess return values
    """

    test_case_output_path_reference = output_path_reference.joinpath(test_case_name)
    test_case_output_path_betterproto = output_path_betterproto
    test_case_output_path_betterproto_pyd = output_path_betterproto_pydantic
    test_case_output_path_betterproto_desc = output_path_betterproto_descriptor

    os.makedirs(test_case_output_path_reference, exist_ok=True)
    os.makedirs(test_case_output_path_betterproto, exist_ok=True)
    os.makedirs(test_case_output_path_betterproto_pyd, exist_ok=True)
    os.makedirs(test_case_output_path_betterproto_desc, exist_ok=True)

    clear_directory(test_case_output_path_reference)
    clear_directory(test_case_output_path_betterproto)
    clear_directory(test_case_output_path_betterproto_pyd)
    clear_directory(test_case_output_path_betterproto_desc)

    (
        (ref_out, ref_err, ref_code),
        (plg_out, plg_err, plg_code),
        (plg_out_pyd, plg_err_pyd, plg_code_pyd),
        (plg_out_desc, plg_err_desc, plg_code_desc),
    ) = await asyncio.gather(
        protoc(test_case_input_path, test_case_output_path_reference, True),
        protoc(test_case_input_path, test_case_output_path_betterproto, False),
        protoc(test_case_input_path, test_case_output_path_betterproto_pyd, False, True),
        protoc(test_case_input_path, test_case_output_path_betterproto_desc, False, False, True),
    )

    if ref_code == 0:
        print(f"\033[31;1;4mGenerated reference output for {test_case_name!r}\033[0m")
    else:
        print(f"\033[31;1;4mFailed to generate reference output for {test_case_name!r}\033[0m")
        print(ref_err.decode())

    if verbose:
        if ref_out:
            print("Reference stdout:")
            sys.stdout.buffer.write(ref_out)
            sys.stdout.buffer.flush()

        if ref_err:
            print("Reference stderr:")
            sys.stderr.buffer.write(ref_err)
            sys.stderr.buffer.flush()

    if plg_code == 0:
        print(f"\033[31;1;4mGenerated plugin output for {test_case_name!r}\033[0m")
    else:
        print(f"\033[31;1;4mFailed to generate plugin output for {test_case_name!r}\033[0m")
        print(plg_err.decode())

    if verbose:
        if plg_out:
            print("Plugin stdout:")
            sys.stdout.buffer.write(plg_out)
            sys.stdout.buffer.flush()

        if plg_err:
            print("Plugin stderr:")
            sys.stderr.buffer.write(plg_err)
            sys.stderr.buffer.flush()

    if plg_code_pyd == 0:
        print(f"\033[31;1;4mGenerated plugin (pydantic compatible) output for {test_case_name!r}\033[0m")
    else:
        print(f"\033[31;1;4mFailed to generate plugin (pydantic compatible) output for {test_case_name!r}\033[0m")
        print(plg_err_pyd.decode())

    if verbose:
        if plg_out_pyd:
            print("Plugin stdout:")
            sys.stdout.buffer.write(plg_out_pyd)
            sys.stdout.buffer.flush()

        if plg_err_pyd:
            print("Plugin stderr:")
            sys.stderr.buffer.write(plg_err_pyd)
            sys.stderr.buffer.flush()

    if plg_code_desc == 0:
        print(f"\033[31;1;4mGenerated plugin (google protobuf descriptor) output for {test_case_name!r}\033[0m")
    else:
        print(
            f"\033[31;1;4mFailed to generate plugin (google protobuf descriptor) output for {test_case_name!r}\033[0m"
        )
        print(plg_err_desc.decode())

    if verbose:
        if plg_out_desc:
            print("Plugin stdout:")
            sys.stdout.buffer.write(plg_out_desc)
            sys.stdout.buffer.flush()

        if plg_err_desc:
            print("Plugin stderr:")
            sys.stderr.buffer.write(plg_err_desc)
            sys.stderr.buffer.flush()

    return max(ref_code, plg_code, plg_code_pyd, plg_code_desc)


def main():
    if sys.argv[1:2] == ["-v"]:
        verbose = True
    else:
        verbose = False

    asyncio.run(generate(verbose))


if __name__ == "__main__":
    main()
