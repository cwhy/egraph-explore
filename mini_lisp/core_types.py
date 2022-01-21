from __future__ import annotations

from typing import TypeVar, runtime_checkable, Protocol, Tuple, Union, NamedTuple

T = TypeVar("T")


class Symbol(NamedTuple):
    index: int

    def __str__(self):
        if self.index == 0:
            return chr(0x24EA)
        elif self.index <= 20:
            return chr(0x245f + self.index)
        elif self.index <= 35:
            return chr(0x323C + self.index)
        elif self.index <= 50:
            return chr(0x328D + self.index)
        else:
            return f"({self.index})"


@runtime_checkable
class AstType(Protocol[T]):
    args: Tuple[Union[int, float, str, Symbol, T], ...]
