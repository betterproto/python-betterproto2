# Better Protobuf / gRPC Support for Python

![](https://github.com/betterproto/python-betterproto2/actions/workflows/ci.yml/badge.svg)

> :warning: `betterproto2` is a fork of the original [`betterproto`](https://github.com/danielgtaylor/python-betterproto) repository. It is a major redesign of the library, allowing to fix several bugs and to support new features.
> 
> However, it is still in active developement. The documentation is not complete, there is still work to do and the project is still subject to breaking changes.

This project aims to provide an improved experience when using Protobuf / gRPC in a modern Python environment by making use of modern language features and generating readable, understandable, idiomatic Python code. It will not support legacy features or environments (e.g. Protobuf 2). The following are supported:

- Protobuf 3 & gRPC code generation
  - Both binary & JSON serialization is built-in
- Python 3.7+ making use of:
  - Enums
  - Dataclasses
  - `async`/`await`
  - Timezone-aware `datetime` and `timedelta` objects
  - Relative imports
  - Mypy type checking
- [Pydantic Models](https://docs.pydantic.dev/) generation


## Motivation

This project exists because of the following limitations of the Google protoc plugin for Python.

- No `async` support (requires additional `grpclib` plugin)
- No typing support or code completion/intelligence (requires additional `mypy` plugin)
- No `__init__.py` module files get generated
- Output is not importable
  - Import paths break in Python 3 unless you mess with `sys.path`
- Bugs when names clash (e.g. `codecs` package)
- Generated code is not idiomatic
  - Completely unreadable runtime code-generation
  - Much code looks like C++ or Java ported 1:1 to Python
  - Capitalized function names like `HasField()` and `SerializeToString()`
  - Uses `SerializeToString()` rather than the built-in `__bytes__()`
  - Special wrapped types don't use Python's `None`
  - Timestamp/duration types don't use Python's built-in `datetime` module

This project is a reimplementation from the ground up focused on idiomatic modern Python to help fix some of the above. While it may not be a 1:1 drop-in replacement due to changed method names and call patterns, the wire format is identical.

## Documentation

The documentation of betterproto is available online: https://betterproto.github.io/python-betterproto2/

## Development

- _Join us on [Discord](https://discord.gg/DEVteTupPb)!_

### Requirements

- Python (3.10 or higher)

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
  *Modern Python package and project manager*

- [poethepoet](https://github.com/nat-n/poethepoet) for running development tasks as defined in pyproject.toml
  - Can be installed to your host environment via `pip install poethepoet` then executed as simple `poe`
  - or run from the uv environment as `uv run poe`

### Getting Started

This project uses a uv workspace with two packages:
- `betterproto2` - The main library
- `betterproto2_compiler` - The protoc plugin

```bash
# Install dependencies and sync the workspace
uv sync

# Build all packages
uv build --all-packages

# Set up test outputs (required before running tests)
# Note: This requires grpcio-tools to be installed
cd betterproto2_compiler && uv run poe generate
cd ../betterproto2 && uv run poe get-local-compiled-tests
cd ..

# Run tests (after setting up test outputs)
uv run poe test

# Format code using ruff directly
uv run ruff format betterproto2/src betterproto2/tests betterproto2_compiler/src betterproto2_compiler/tests

# Check code using ruff directly  
uv run ruff check betterproto2/src betterproto2/tests betterproto2_compiler/src betterproto2_compiler/tests
```

### Notes

- The workspace-level poe tasks (format, check) reference directories that don't exist at the workspace root, so use the direct ruff commands shown above.
- The workspace-level `uv run poe test` command runs tests for both packages sequentially.
- Individual packages have their own specific tasks - check `uv run poe --help` from within each package directory for more options.
- Some tests may fail due to missing test data files (like in `test_streams.py`), but the core functionality tests should pass.

## License

Copyright © 2019 Daniel G. Taylor

Copyright © 2024 The betterproto contributors
