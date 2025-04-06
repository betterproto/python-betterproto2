# Clients

!!! warning
    Make sure to enable client generation when compiling your code. See [TODO link]

## Synchronous clients

Compile the following proto file in a directory called `example`, with the generation of synchronous clients activated.

```proto
syntax = "proto3";

message Request {}
message Response {}

service MyService {
    rpc MyRPC(Request) returns (Response);
}
```

The synchronous client can be used as follows:

```python
import grpc

from example import Request, MyServiceStub

with grpc.insecure_channel("address:port") as channel:
    client = MyServiceStub(channel)

    response = client.my_rpc(Request())
```

## Asynchronous clients

### With grpcio

!!! warning
    No yet supported

### With grpclib

!!! warning
    Documentation not yet available
