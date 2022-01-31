from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, runtime_checkable, Protocol, Tuple, Union, NamedTuple, Literal


class Symbol(NamedTuple):
    i: int
    type: Literal["symbol"] = "symbol"

    @property
    def display(self) -> str:
        return str(self) + " "

    def __str__(self) -> str:
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

    @property
    def display(self) -> str:
        return f"{self.value:.2f}"


class Variable(NamedTuple):
    name: str
    type: Literal["variable"] = "variable"

    @property
    def display(self) -> str:
        return f"{self.name}"


@runtime_checkable
class AstLeaf(Protocol):
    @property
    @abstractmethod
    def type(self) -> AstLeafType: ...

    @property
    @abstractmethod
    def display(self) -> str: ...


T = TypeVar("T", covariant=True, bound=AstLeaf)


@runtime_checkable
class AstParent(Protocol[T]):
    @property
    @abstractmethod
    def args(self) -> Tuple[Union[AstParent[T], T], ...]: ...

    @property
    @abstractmethod
    def type(self) -> Literal["ast_parent"]: ...

    def __new__(cls, args: Tuple[Union[AstParent[T], T], ...]) -> AstParent: ...

    @property
    @abstractmethod
    def display(self) -> str: ...


AstNode = Union[T, AstParent[T]]
