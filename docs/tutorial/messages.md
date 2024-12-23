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