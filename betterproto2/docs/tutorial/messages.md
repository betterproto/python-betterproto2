# Messages

A protobuf message is represented by a class that inherit from the `betterproto2.Message` abstract class.

## Field presence

The [documentation](https://protobuf.dev/programming-guides/field_presence/) of protobuf defines field presence as "the
notion of whether a protobuf field has a value". The presence of a field can be tracked in two ways:

 - **Implicit presence.** It is not possible to know if the field was set to its default value or if it was simply
   omitted. When the field is omitted, it is set to its default value automatically (`0` for an `int`, `""` for a
   string, ...)
 - **Explicit presence.** It is possible to know if the field was set to its default value or if it was
   omitted. In Python, these fields are marked as optional. They are set to `None` when omitted.

The [documentation](https://protobuf.dev/programming-guides/field_presence/#presence-in-proto3-apis) of protobuf shows
when field presence is explicitly tracked.

For example, given the following `proto` file:

```proto
syntax = "proto3";

message Message {
    int32 x = 1;
    optional int32 y = 2;
}
```

We can see that the default values are not the same:

```python
>>> msg = Message()
>>> print(msg.x)
0
>>> print(msg.y)
None
```

!!! warning
    When a field is a message, its presence is always tracked explicitly even if it is not marked as optional. Marking a
    message field as optional has no effect: the default value of such a field is always `None`, not an empty message.

## Oneof support

Protobuf supports grouping fields in a `oneof` clause: at most one of the fields in the group can be set at the same
time. Let's use the following `proto`:

```proto
syntax = "proto3";

message Test {
    oneof group {
        bool a = 1;
        int32 b = 2;
        string c = 3;
    }
}
```

The `betterproto2.which_one_of` function allows finding which one of the fields of the `oneof` group is set. The
function returns the name of the field that is set, and the value of the field.

```python
>>> betterproto2.which_one_of(Message(a=True), group_name="group")
('a', True)
>>> betterproto2.which_one_of(Message(), group_name="group")
('', None)
```

On Python 3.10 and later, it is also possible to use a `match` statement to find which item in a `oneof` group is active.

```python
>>> def find(m: Message) -> str:
...     match m:
...         case Message(a=bool(value)):
...             return f"a is set to {value}"
...         case Message(b=int(value)):
...             return f"b is set to {value}"
...     return "No field set"
...
>>> find(Message(a=True))
'a is set to True'
>>> find(Message(b=12))
'b is set to 12'
>>> find(Message())
'No field set'
```

## Unwrapping optional values

In protobuf, fields are often marked as optional, either manually or because it is the default behavior of the protocol.
If you care about type-checking, this can be tedious to handle as you need to make sure each field is not `None` before
using, even when you know that the field will never be `None` is your application.

```python
# typing error: item "None" of "Message | None" has no attribute "field"
message.msg_field.field
```

To simplify this, betterproto provides a convenience function: `unwrap`. This function takes an optional value, and
returns the same value if it is not `None`. If the value is `None`, an error is raised.

```python
from betterproto2 import unwrap

# no typing error!
unwrap(message.msg_field).field
```
