Migration Guide
===============

## Google's protocolbuffers

betterproto has a mostly 1 to 1 drop in replacement for Google's protocolbuffers (after
regenerating your protobufs of course) although there are some minor differences.

!!! note

    betterproto implements the same basic methods including:

    - `betterproto.Message.FromString`
    - `betterproto.Message.SerializeToString`

    for compatibility purposes, however it is important to note that these are
    effectively aliases for `betterproto.Message.parse` and
    `betterproto.Message.__bytes__` respectively.


## One-of Support

Protobuf supports grouping fields in a oneof clause. Only one of the fields in the group
may be set at a given time. For example, given the proto:

```proto
syntax = "proto3";

message Test {
  oneof foo {
    bool on = 1;
    int32 count = 2;
    string name = 3;
  }
}
```

You can use `betterproto.which_one_of(message, group_name)` to determine which of the
fields was set. It returns a tuple of the field name and value, or a blank string and
`None` if unset. Again this is a little different than the official Google code
generator:

```python
# Old way (official Google protobuf package)
>>> message.WhichOneof("group")
"foo"

# New way (this project)
>>> betterproto.which_one_of(message, "group")
("foo", "foo's value")
```


## Well-Known Google Types

Google provides several well-known message types like a timestamp, duration, and several
wrappers used to provide optional zero value support. Each of these has a special JSON
representation and is handled a little differently from normal messages. The Python
mapping for these is as follows:

| Google Message                | Python Type                                    | Default                  |
|-------------------------------|------------------------------------------------|--------------------------|
| `google.protobuf.duration`    | `datetime.timedelta`                           | `0`                      |
| `google.protobuf.timestamp`   | Timezone-aware `datetime.datetime`             | `1970-01-01T00:00:00Z`   |
| `google.protobuf.*Value`      | `Optional[...]` / `None`                       | `None`                   |
| `google.protobuf.*`           | `betterproto.lib.std.google.protobuf.*`        | `None`                   |
| `google.protobuf.*`           | `betterproto.lib.pydantic.google.protobuf.*`   | `None`                   |

For the wrapper types, the Python type corresponds to the wrapped type, e.g.
``google.protobuf.BoolValue`` becomes ``Optional[bool]`` while
``google.protobuf.Int32Value`` becomes ``Optional[int]``. All of the optional values
default to None, so don't forget to check for that possible state.

Given:

```proto
syntax = "proto3";

import "google/protobuf/duration.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/wrappers.proto";

message Test {
  google.protobuf.BoolValue maybe = 1;
  google.protobuf.Timestamp ts = 2;
  google.protobuf.Duration duration = 3;
}
```

You can use it as such:

```python
>>> t = Test().from_dict({"maybe": True, "ts": "2019-01-01T12:00:00Z", "duration": "1.200s"})
>>> t
Test(maybe=True, ts=datetime.datetime(2019, 1, 1, 12, 0, tzinfo=datetime.timezone.utc), duration=datetime.timedelta(seconds=1, microseconds=200000))

>>> t.ts - t.duration
datetime.datetime(2019, 1, 1, 11, 59, 58, 800000, tzinfo=datetime.timezone.utc)

>>> t.ts.isoformat()
'2019-01-01T12:00:00+00:00'

>>> t.maybe = None
>>> t.to_dict()
{'ts': '2019-01-01T12:00:00Z', 'duration': '1.200s'}
```


## [1.2.5] to [2.0.0b1]

### Updated package structures

Generated code now strictly follows the *package structure* of the `.proto` files.
Consequently `.proto` files without a package will be combined in a single
`__init__.py` file. To avoid overwriting existing `__init__.py` files, its best
to compile into a dedicated subdirectory.

Upgrading:

- Remove your previously compiled `.py` files.
- Create a new *empty* directory, e.g. `generated` or `lib/generated/proto` etc.
- Regenerate your python files into this directory
- Update import statements, e.g. `import ExampleMessage from generated`
