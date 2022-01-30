from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, runtime_checkable, Protocol, Tuple, Union, NamedTuple, Literal


class Symbol(NamedTuple):
    i: int
    type: Literal["symbol"] = "symbol"

    def __str__(self):
        if self.i == 0:
            return chr(0x24EA)
        elif self.i <= 20:
            return chr(0x245f + self.i)
        elif self.i <= 35:
            return chr(0x323C + self.i)
        elif self.i <= 50:
            return chr(0x328D + self.i)
        else:
            return f"({self.i})"


AstLeafType = Literal["float", "variable", "symbol"]


class Float(NamedTuple):
    value: float
    type: Literal["float"] = "float"


class Variable(NamedTuple):
    name: str
    type: Literal["variable"] = "variable"


@runtime_checkable
class AstLeaf(Protocol):
    @abstractmethod
    @property
    def type(self) -> AstLeafType: ...


T = TypeVar("T", covariant=True, bound=AstLeaf)


@runtime_checkable
class AstParent(Protocol[T]):
    @abstractmethod
    @property
    def args(self) -> Tuple[Union[AstParent[T], T], ...]: ...

    @abstractmethod
    @property
    def type(self) -> Literal["ast_parent"]: ...

    def __new__(cls, args: Tuple[Union[AstParent[T], T], ...]) -> AstParent: ...


AstNode = Union[T, AstParent[T]]

