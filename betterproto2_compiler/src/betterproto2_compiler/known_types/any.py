import typing

import betterproto2
from typing_extensions import Self

from betterproto2_compiler.lib.google.protobuf import Any as VanillaAny

default_message_pool = betterproto2.MessagePool()  # Only for typing purpose


class Any(VanillaAny):
    @classmethod
    def pack(cls, message: betterproto2.Message, message_pool: "betterproto2.MessagePool | None" = None) -> "Any":
        """
        Pack the given message in the `Any` object.

        The message type must be registered in the message pool, which is done automatically when the module defining
        the message type is imported.
        """
        message_pool = message_pool or default_message_pool

        type_url = message_pool.type_to_url[type(message)]
        value = bytes(message)

        return cls(type_url=type_url, value=value)

    def unpack(self, message_pool: "betterproto2.MessagePool | None" = None) -> betterproto2.Message | None:
        """
        Return the message packed inside the `Any` object.

        The target message type must be registered in the message pool, which is done automatically when the module
        defining the message type is imported.
        """
        if not self.type_url:
            return None

        message_pool = message_pool or default_message_pool

        try:
            message_type = message_pool.url_to_type[self.type_url]
        except KeyError:
            raise TypeError(f"Can't unpack unregistered type: {self.type_url}")

        return message_type.parse(self.value)

    def to_dict(self, **kwargs) -> dict[str, typing.Any]:
        # TODO allow passing a message pool to `to_dict`
        output: dict[str, typing.Any] = {"@type": self.type_url}

        value = self.unpack()

        if value is None:
            return output

        if type(value).to_dict == betterproto2.Message.to_dict:
            output.update(value.to_dict(**kwargs))
        else:
            output["value"] = value.to_dict(**kwargs)

        return output

    # TODO typing
    @classmethod
    def from_dict(cls, value, *, ignore_unknown_fields: bool = False) -> Self:
        value = dict(value)  # Make a copy

        type_url = value.pop("@type", None)
        msg_cls = default_message_pool.url_to_type.get(type_url, None)

        if not msg_cls:
            raise TypeError(f"Can't unpack unregistered type: {type_url}")

        if not msg_cls.to_dict == betterproto2.Message.to_dict:
            value = value["value"]

        return cls(
            type_url=type_url, value=bytes(msg_cls.from_dict(value, ignore_unknown_fields=ignore_unknown_fields))
        )
