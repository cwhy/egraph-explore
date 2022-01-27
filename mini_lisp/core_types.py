from __future__ import annotations

from typing import TypeVar, runtime_checkable, Protocol, Tuple, Union, NamedTuple, Literal


class Symbol(NamedTuple):
    index: int
    type: Literal["symbol"] = "symbol"

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


AstLeafType = Literal["float", "variable", "symbol"]


class Float(NamedTuple):
    value: float
    type: Literal["float"] = "float"


class Variable(NamedTuple):
    name: str
    type: Literal["variable"] = "variable"


@runtime_checkable
class AstLeaf(Protocol):
    type: AstLeafType


T = TypeVar("T", bound=AstLeaf)


@runtime_checkable
class AstParent(Protocol[T]):
    args: Tuple[T, ...]
    type: Literal["ast_parent"] = "ast_parent"


TP = TypeVar("TP", bound=AstParent)

AstNode = Union[T, AstParent[T]]
