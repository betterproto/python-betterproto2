# Better Protobuf / gRPC Support for Python

![](https://github.com/betterproto/python-betterproto2/actions/workflows/ci.yml/badge.svg)

> :warning: `betterproto2` is a fork of the original [`betterproto`](https://github.com/danielgtaylor/python-betterproto) repository. It is a major redesign of the library, allowing to fix several bugs and to support new features.
> 
> However, it is still in active developement. The documentation is not complete and a few breaking changes still are likely to be done, but there is still work to do and the project is still subject to breaking changes.

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

- Python (3.8 or higher)

- [poetry](https://python-poetry.org/docs/#installation)
  *Needed to install dependencies in a virtual environment*

- [poethepoet](https://github.com/nat-n/poethepoet) for running development tasks as defined in pyproject.toml
  - Can be installed to your host environment via `pip install poethepoet` then executed as simple `poe`
  - or run from the poetry venv as `poetry run poe`

### Setup

```sh
# Get set up with the virtual env & dependencies
poetry install -E compiler

# Activate the poetry environment
poetry shell
```

### Code style

This project enforces [black](https://github.com/psf/black) python code formatting.

Before committing changes run:

```sh
poe format
```

To avoid merge conflicts later, non-black formatted python code will fail in CI.

### Tests

There are two types of tests:

1. Standard tests
2. Custom tests

#### Standard tests

Adding a standard test case is easy.

- Create a new directory `betterproto/tests/inputs/<name>`
  - add `<name>.proto`  with a message called `Test`
  - add `<name>.json` with some test data (optional)

It will be picked up automatically when you run the tests.

- See also: [Standard Tests Development Guide](tests/README.md)

#### Custom tests

Custom tests are found in `tests/test_*.py` and are run with pytest.

#### Running

Here's how to run the tests.

```sh
# Generate assets from sample .proto files required by the tests
poe generate
# Run the tests
poe test
```

To run tests as they are run in CI (with tox) run:

```sh
poe full-test
```

### (Re)compiling Google Well-known Types

Betterproto includes compiled versions for Google's well-known types at [src/betterproto/lib/google](src/betterproto/lib/google).
Be sure to regenerate these files when modifying the plugin output format, and validate by running the tests.

Normally, the plugin does not compile any references to `google.protobuf`, since they are pre-compiled. To force compilation of `google.protobuf`, use the option `--custom_opt=INCLUDE_GOOGLE`.

Assuming your `google.protobuf` source files (included with all releases of `protoc`) are located in `/usr/local/include`, you can regenerate them as follows:

```sh
protoc \
    --plugin=protoc-gen-custom=src/betterproto/plugin/main.py \
    --custom_opt=INCLUDE_GOOGLE \
    --custom_out=src/betterproto/lib \
    -I /usr/local/include/ \
    /usr/local/include/google/protobuf/*.proto
```

### TODO

- [x] Fixed length fields
  - [x] Packed fixed-length
- [x] Zig-zag signed fields (sint32, sint64)
- [x] Don't encode zero values for nested types
- [x] Enums
- [x] Repeated message fields
- [x] Maps
  - [x] Maps of message fields
- [x] Support passthrough of unknown fields
- [x] Refs to nested types
- [x] Imports in proto files
- [x] Well-known Google types
  - [ ] Support as request input
  - [ ] Support as response output
    - [ ] Automatically wrap/unwrap responses
- [x] OneOf support
  - [x] Basic support on the wire
  - [x] Check which was set from the group
  - [x] Setting one unsets the others
- [ ] JSON that isn't completely naive.
  - [x] 64-bit ints as strings
  - [x] Maps
  - [x] Lists
  - [x] Bytes as base64
  - [ ] Any support
  - [x] Enum strings
  - [x] Well known types support (timestamp, duration, wrappers)
  - [x] Support different casing (orig vs. camel vs. others?)
- [x] Async service stubs
  - [x] Unary-unary
  - [x] Server streaming response
  - [x] Client streaming request
- [x] Renaming messages and fields to conform to Python name standards
- [x] Renaming clashes with language keywords
- [x] Python package
- [x] Automate running tests
- [ ] Cleanup!

## License

Copyright © 2019 Daniel G. Taylor

Copyright © 2024 The betterproto contributors
