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

- [poetry](https://python-poetry.org/docs/#installation)
  *Needed to install dependencies in a virtual environment*

- [poethepoet](https://github.com/nat-n/poethepoet) for running development tasks as defined in pyproject.toml
  - Can be installed to your host environment via `pip install poethepoet` then executed as simple `poe`
  - or run from the poetry venv as `poetry run poe`

## License

Copyright © 2019 Daniel G. Taylor

Copyright © 2024 The betterproto contributors
