Getting Started
===============

## Installation

The package `betterproto2` can be simply installed from PyPI using `pip`:

```sh
pip install betterproto2[all]
```

!!! info
    The package is compatible with all Python versions from 3.10 to 3.13.


## Compiling proto files

Follow the documentation of [betterproto2 compiler](https://betterproto.github.io/python-betterproto2-compiler/getting-started/) to compile your proto files.

!!! warning
    Make sure that the proto files were generated with a version of `betterproto2_compiler` that is compatible with your
    version of `betterproto2`.

    The version `0.x.y` of `betterproto` is compatible with the version `0.a.b` of the compiler if and only if `a=b`.


## Basic usage

If you successfuly compiled the `example.proto` file from the compiler documentation, you should now be able to use it!

```python
>>> from lib.helloworld import HelloWorld
>>> msg = HelloWorld(message="Hello world!")
>>> msg
HelloWorld(message='Hello world!')
>>> bytes(msg)
b'\n\x0cHello world!'
>>> msg.to_dict()
{'message': 'Hello world!'}
```

!!! Warning
    The rest of the documentation is not up to date.


## Async gRPC Support

The generated code includes [grpclib](https://grpclib.readthedocs.io/en/latest) based
stub (client and server) classes for rpc services declared in the input proto files.
It is enabled by default.


Given a service definition similar to the one below:

```proto
syntax = "proto3";

package echo;

message EchoRequest {
    string value = 1;
    // Number of extra times to echo
    uint32 extra_times = 2;
}

message EchoResponse {
    repeated string values = 1;
}

message EchoStreamResponse  {
    string value = 1;
}

service Echo {
    rpc Echo(EchoRequest) returns (EchoResponse);
    rpc EchoStream(EchoRequest) returns (stream EchoStreamResponse);
}
```

The generated client can be used like so:

```python
import asyncio
from grpclib.client import Channel
import echo


async def main():
    channel = Channel(host="127.0.0.1", port=50051)
    service = echo.EchoStub(channel)
    response = await service.echo(value="hello", extra_times=1)
    print(response)

    async for response in service.echo_stream(value="hello", extra_times=1):
        print(response)

    # don't forget to close the channel when you're done!
    channel.close()

asyncio.run(main())

# outputs
EchoResponse(values=['hello', 'hello'])
EchoStreamResponse(value='hello')
EchoStreamResponse(value='hello')
```


The server-facing stubs can be used to implement a Python
gRPC server.
To use them, simply subclass the base class in the generated files and override the
service methods:

```python
from echo import EchoBase
from grpclib.server import Server
from typing import AsyncIterator


class EchoService(EchoBase):
    async def echo(self, value: str, extra_times: int) -> "EchoResponse":
        return value

    async def echo_stream(
        self, value: str, extra_times: int
    ) -> AsyncIterator["EchoStreamResponse"]:
        for _ in range(extra_times):
            yield value


async def start_server():
    HOST = "127.0.0.1"
    PORT = 1337
    server = Server([EchoService()])
    await server.start(HOST, PORT)
    await server.serve_forever()
```

## JSON

Message objects include `betterproto.Message.to_json` and
`betterproto.Message.from_json` methods for JSON (de)serialisation, and
`betterproto.Message.to_dict`, `betterproto.Message.from_dict` for
converting back and forth from JSON serializable dicts.

For compatibility the default is to convert field names to
`betterproto.Casing.CAMEL`. You can control this behavior by passing a
different casing value, e.g:

```python
@dataclass
class MyMessage(betterproto.Message):
    a_long_field_name: str = betterproto.string_field(1)


>>> test = MyMessage(a_long_field_name="Hello World!")
>>> test.to_dict(betterproto.Casing.SNAKE)
{"a_long_field_name": "Hello World!"}
>>> test.to_dict(betterproto.Casing.CAMEL)
{"aLongFieldName": "Hello World!"}

>>> test.to_json(indent=2)
'{\n  "aLongFieldName": "Hello World!"\n}'

>>> test.from_dict({"aLongFieldName": "Goodbye World!"})
>>> test.a_long_field_name
"Goodbye World!"
```
