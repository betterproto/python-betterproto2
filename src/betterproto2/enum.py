from enum import IntEnum

from typing_extensions import Self


class Enum(IntEnum):
    @classmethod
    def _missing_(cls, value):
        # Create a new "unknown" instance with the given value.
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._name_ = None
        return obj

    def __str__(self):
        if self.name is None:
            return f"{self.__class__.__name__}.~UNKNOWN({self.value})"
        return f"{self.__class__.__name__}.{self.name}"

    def __repr__(self):
        if self.name is None:
            return f"<{self.__class__.__name__}.~UNKNOWN: {self.value}>"
        return super().__repr__()

    @classmethod
    def try_value(cls, value: int = 0) -> Self:
        """Return the value which corresponds to the value.

        Parameters
        -----------
        value: :class:`int`
            The value of the enum member to get.

        Returns
        -------
        :class:`Enum`
            The corresponding member or a new instance of the enum if
            ``value`` isn't actually a member.
        """
        return cls(value)

    @classmethod
    def from_string(cls, name: str) -> Self:
        """Return the value which corresponds to the string name.

        Parameters
        -----------
        name: :class:`str`
            The name of the enum member to get.

        Raises
        -------
        :exc:`ValueError`
            The member was not found in the Enum.
        """
        try:
            return cls._member_map_[name]
        except KeyError as e:
            raise ValueError(f"Unknown value {name} for enum {cls.__name__}") from e
