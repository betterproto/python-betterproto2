import asyncio
import atexit
import importlib
import os
import platform
import sys
import tempfile
from collections.abc import Callable, Generator
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

root_path = Path(__file__).resolve().parent
inputs_path = root_path.joinpath("inputs")
output_path_reference = root_path.joinpath("output_reference")
output_path_betterproto = root_path.joinpath("output_betterproto")
output_path_betterproto_pydantic = root_path.joinpath("output_betterproto_pydantic")


def get_files(path, suffix: str) -> Generator[str, None, None]:
    for r, dirs, files in os.walk(path):
        for filename in [f for f in files if f.endswith(suffix)]:
            yield os.path.join(r, filename)


def get_directories(path):
    for root, directories, files in os.walk(path):
        yield from directories


async def protoc(
    path: str | Path,
    output_dir: str | Path,
    reference: bool = False,
    pydantic_dataclasses: bool = False,
):
    path: Path = Path(path).resolve()
    output_dir: Path = Path(output_dir).resolve()
    python_out_option: str = "python_betterproto_out" if not reference else "python_out"

    if pydantic_dataclasses:
        plugin_path = Path("src/betterproto2/plugin/main.py")

        if "Win" in platform.system():
            with tempfile.NamedTemporaryFile("w", encoding="UTF-8", suffix=".bat", delete=False) as tf:
                # See https://stackoverflow.com/a/42622705
                tf.writelines(
                    [
                        "@echo off",
                        f"\nchdir {os.getcwd()}",
                        f"\n{sys.executable} -u {plugin_path.as_posix()}",
                    ]
                )

                tf.flush()

                plugin_path = Path(tf.name)
                atexit.register(os.remove, plugin_path)

        command = [
            sys.executable,
            "-m",
            "grpc.tools.protoc",
            f"--plugin=protoc-gen-custom={plugin_path.as_posix()}",
            "--experimental_allow_proto3_optional",
            "--custom_opt=pydantic_dataclasses",
            f"--proto_path={path.as_posix()}",
            f"--custom_out={output_dir.as_posix()}",
            *[p.as_posix() for p in path.glob("*.proto")],
        ]
    else:
        command = [
            sys.executable,
            "-m",
            "grpc.tools.protoc",
            f"--proto_path={path.as_posix()}",
            f"--{python_out_option}={output_dir.as_posix()}",
            *[p.as_posix() for p in path.glob("*.proto")],
        ]
    proc = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout, stderr, proc.returncode


@dataclass
class TestCaseJsonFile:
    json: str
    test_name: str
    file_name: str

    def belongs_to(self, non_symmetrical_json: dict[str, tuple[str, ...]]) -> bool:
        return self.file_name in non_symmetrical_json.get(self.test_name, ())


def get_test_case_json_data(test_case_name: str, *json_file_names: str) -> list[TestCaseJsonFile]:
    """
    :return:
        A list of all files found in "{inputs_path}/test_case_name" with names matching
        f"{test_case_name}.json" or f"{test_case_name}_*.json", OR given by
        json_file_names
    """
    test_case_dir = inputs_path.joinpath(test_case_name)
    possible_file_paths = [
        *(test_case_dir.joinpath(json_file_name) for json_file_name in json_file_names),
        test_case_dir.joinpath(f"{test_case_name}.json"),
        *test_case_dir.glob(f"{test_case_name}_*.json"),
    ]

    result = []
    for test_data_file_path in possible_file_paths:
        if not test_data_file_path.exists():
            continue
        with test_data_file_path.open("r") as fh:
            result.append(TestCaseJsonFile(fh.read(), test_case_name, test_data_file_path.name.split(".")[0]))

    return result


def find_module(module: ModuleType, predicate: Callable[[ModuleType], bool]) -> ModuleType | None:
    """
    Recursively search module tree for a module that matches the search predicate.
    Assumes that the submodules are directories containing __init__.py.

    Example:

        # find module inside foo that contains Test
        import foo
        test_module = find_module(foo, lambda m: hasattr(m, 'Test'))
    """
    if predicate(module):
        return module

    module_path = Path(*module.__path__)

    for sub in [sub.parent for sub in module_path.glob("**/__init__.py")]:
        if sub == module_path:
            continue
        sub_module_path = sub.relative_to(module_path)
        sub_module_name = ".".join(sub_module_path.parts)

        sub_module = importlib.import_module(f".{sub_module_name}", module.__name__)

        if predicate(sub_module):
            return sub_module

    return None
