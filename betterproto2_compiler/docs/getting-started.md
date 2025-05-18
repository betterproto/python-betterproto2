# Getting started

## Install protoc

The betterproto2 compiler is a plugin of `protoc`, you first need to [install](https://grpc.io/docs/protoc-installation/) it.

You can also use it from `grpcio-tools`:

```sh
pip install grpcio-tools
```

## Install `betterproto2_compiler`

It is possible to install `betterproto2_compiler` using pip:

```
pip install betterproto2_compiler
```

## Compile a proto file

Create the following `example.proto` file.

```proto
syntax = "proto3";

package helloworld;

message HelloWorld {
    string message = 1;
}

service HelloService {
    rpc SayHello (HelloWorld) returns (HelloWorld);
}
```

You should now be able to compile it using:

```
mkdir lib
protoc -I . --python_betterproto2_out=lib example.proto
```

If you installed `protoc` with `grpc-tools`, the command will be:

```
mkdir lib
python -m grpc.tools.protoc -I . --python_betterproto2_out=lib example.proto
```

### Service compilation

#### Clients

By default, for each service, betterproto will generate a synchronous client. Both synchronous and asynchronous clients
are supported.

  - Synchronous clients rely on the `grpcio` package. Make sure to enable the `grpcio` extra package when installing
    betterproto2 to use them.
  - Asynchronous clients rely on the `grpclib` package. Make sure to enable the `grpclib` extra package when installing
    betterproto2 to use them.

To choose which clients to generate, use the `client_generation` option of betterproto. It supports the following
values:

  - `none`: Clients are not generated.
  - `sync`: Only synchronous clients are generated.
  - `async`: Only asynchronous clients are generated.
  - `sync_async`: Both synchronous and asynchronous clients are generated.
        Asynchronous clients are generated with the Async suffix.
  - `async_sync`: Both synchronous and asynchronous clients are generated.
        Synchronous clients are generated with the Sync suffix.
  - `sync_async_no_default`: Both synchronous and asynchronous clients are generated.
        Synchronous clients are generated with the Sync suffix, and asynchronous clients are generated with the Async
        suffix.

For example, `protoc -I . --python_betterproto2_out=lib example.proto --python_betterproto2_opt=client_generation=async`
will only generate asynchronous clients.

#### Servers

By default, betterproto will not generate server base classes. To enable them, set the `server_generation` option to
`async` with `--python_betterproto2_opt=server_generation=async`.

These base classes will be asynchronous and rely on `grpclib`. To use them, make sure to install `betterproto2` with the
`grpclib` extra package.
