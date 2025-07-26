import asyncio
import os
import sys
from pathlib import Path

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


async def protoc(
    path: str | Path,
    output_dir: str | Path,
    reference: bool = False,
    pydantic_dataclasses: bool = False,
    google_protobuf_descriptors: bool = False,
):
    resolved_path: Path = Path(path).resolve()
    resolved_output_dir: Path = Path(output_dir).resolve()
    python_out_option: str = "python_out" if reference else "python_betterproto2_out"

    command = [
        sys.executable,
        "-m",
        "grpc.tools.protoc",
        f"--proto_path={resolved_path.as_posix()}",
        f"--{python_out_option}={resolved_output_dir.as_posix()}",
        *[p.as_posix() for p in resolved_path.glob("*.proto")],
    ]

    if not reference:
        command.insert(3, "--python_betterproto2_opt=server_generation=async")
        command.insert(3, "--python_betterproto2_opt=client_generation=async_sync")

        if pydantic_dataclasses:
            command.insert(3, "--python_betterproto2_opt=pydantic_dataclasses")

        if google_protobuf_descriptors:
            command.insert(3, "--python_betterproto2_opt=google_protobuf_descriptors")

    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout, stderr, proc.returncode or 0
