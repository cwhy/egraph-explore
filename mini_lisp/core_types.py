from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, runtime_checkable, Protocol, Tuple, Union, NamedTuple, Literal

from utils.misc import get_rounded_num


class Symbol(NamedTuple):
    i: int
    type: Literal["symbol"] = "symbol"

    @property
    def letter(self) -> str:
        if self.i < 26:
            return chr(97 + self.i)
        else:
            return f"var_{self.i}"

    @property
    def display(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return get_rounded_num(self.i)


AstLeafType = Literal["number", "variable", "symbol"]


class Number(NamedTuple):
    value: Union[float, int]
    type: Literal["number"] = "number"

    @classmethod
    def from_str(cls, token: str) -> Number:
        try:
            return cls(int(token))
        except ValueError:
            try:
                return cls(float(token))
            except ValueError as e:
                raise e

    @property
    def display(self) -> str:
        if isinstance(self.value, int):
            return str(self.value)
        else:
            assert isinstance(self.value, float)
            return f"{self.value:.2f}"


class Variable(NamedTuple):
    name: str
    type: Literal["variable"] = "variable"

    @property
    def display(self) -> str:
        return f"{self.name}"


AT = TypeVar('AT', bound=str, covariant=True)


@runtime_checkable
class AstStuff(Protocol[AT]):
    @property
    @abstractmethod
    def type(self) -> AT: ...

    @property
    @abstractmethod
    def display(self) -> str: ...


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
