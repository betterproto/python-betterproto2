from dataclasses import dataclass
from typing import List

import betterproto2


@dataclass
class TestMessage(betterproto2.Message):
    foo: int = betterproto2.uint32_field(1)
    bar: str = betterproto2.string_field(2)
    baz: float = betterproto2.float_field(3)


@dataclass
class TestNestedChildMessage(betterproto2.Message):
    str_key: str = betterproto2.string_field(1)
    bytes_key: bytes = betterproto2.bytes_field(2)
    bool_key: bool = betterproto2.bool_field(3)
    float_key: float = betterproto2.float_field(4)
    int_key: int = betterproto2.uint64_field(5)


@dataclass
class TestNestedMessage(betterproto2.Message):
    foo: TestNestedChildMessage = betterproto2.message_field(1)
    bar: TestNestedChildMessage = betterproto2.message_field(2)
    baz: TestNestedChildMessage = betterproto2.message_field(3)


@dataclass
class TestRepeatedMessage(betterproto2.Message):
    foo_repeat: List[str] = betterproto2.string_field(1)
    bar_repeat: List[int] = betterproto2.int64_field(2)
    baz_repeat: List[bool] = betterproto2.bool_field(3)


class BenchMessage:
    """Test creation and usage a proto message."""

    def setup(self):
        self.cls = TestMessage
        self.instance = TestMessage()
        self.instance_filled = TestMessage(0, "test", 0.0)
        self.instance_filled_bytes = bytes(self.instance_filled)
        self.instance_filled_nested = TestNestedMessage(
            TestNestedChildMessage("foo", bytearray(b"test1"), True, 0.1234, 500),
            TestNestedChildMessage("bar", bytearray(b"test2"), True, 3.1415, 302),
            TestNestedChildMessage("baz", bytearray(b"test3"), False, 1e5, 300),
        )
        self.instance_filled_nested_bytes = bytes(self.instance_filled_nested)
        self.instance_filled_repeated = TestRepeatedMessage(
            [f"test{i}" for i in range(1_000)],
            [(i - 500) ** 3 for i in range(1_000)],
            [i % 2 == 0 for i in range(1_000)],
        )
        self.instance_filled_repeated_bytes = bytes(self.instance_filled_repeated)

    def time_overhead(self):
        """Overhead in class definition."""

        @dataclass
        class Message(betterproto2.Message):
            foo: int = betterproto2.uint32_field(1)
            bar: str = betterproto2.string_field(2)
            baz: float = betterproto2.float_field(3)

    def time_instantiation(self):
        """Time instantiation"""
        self.cls()

    def time_attribute_access(self):
        """Time to access an attribute"""
        self.instance.foo
        self.instance.bar
        self.instance.baz

    def time_init_with_values(self):
        """Time to set an attribute"""
        self.cls(0, "test", 0.0)

    def time_attribute_setting(self):
        """Time to set attributes"""
        self.instance.foo = 0
        self.instance.bar = "test"
        self.instance.baz = 0.0

    def time_serialize(self):
        """Time serializing a message to wire."""
        bytes(self.instance_filled)

    def time_deserialize(self):
        """Time deserialize a message."""
        TestMessage().parse(self.instance_filled_bytes)

    def time_serialize_nested(self):
        """Time serializing a nested message to wire."""
        bytes(self.instance_filled_nested)

    def time_deserialize_nested(self):
        """Time deserialize a nested message."""
        TestNestedMessage().parse(self.instance_filled_nested_bytes)

    def time_serialize_repeated(self):
        """Time serializing a repeated message to wire."""
        bytes(self.instance_filled_repeated)

    def time_deserialize_repeated(self):
        """Time deserialize a repeated message."""
        TestRepeatedMessage().parse(self.instance_filled_repeated_bytes)


class MemSuite:
    def setup(self):
        self.cls = TestMessage

    def mem_instance(self):
        return self.cls()
