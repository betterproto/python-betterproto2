import asyncio
import os
import sys
from pathlib import Path

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

root_path = Path(__file__).resolve().parent
inputs_path = root_path.joinpath("inputs")
output_path_reference = root_path.joinpath("output_reference")
output_path_betterproto = root_path.joinpath("output_betterproto")
output_path_betterproto_pydantic = root_path.joinpath("output_betterproto_pydantic")


def get_directories(path):
    for root, directories, files in os.walk(path):
        yield from directories


async def protoc(path: str | Path, output_dir: str | Path, reference: bool = False, pydantic_dataclasses: bool = False):
    path: Path = Path(path).resolve()
    output_dir: Path = Path(output_dir).resolve()
    python_out_option: str = "python_out" if reference else "python_betterproto2_out"

    command = [
        sys.executable,
        "-m",
        "grpc.tools.protoc",
        f"--proto_path={path.as_posix()}",
        f"--{python_out_option}={output_dir.as_posix()}",
        *[p.as_posix() for p in path.glob("*.proto")],
    ]

    if not reference:
        command.insert(3, "--python_betterproto2_opt=server_generation=async")
        command.insert(3, "--python_betterproto2_opt=client_generation=async_sync")

        if pydantic_dataclasses:
            command.insert(3, "--python_betterproto2_opt=pydantic_dataclasses")

    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout, stderr, proc.returncode
