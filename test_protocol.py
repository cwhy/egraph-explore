from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar, runtime_checkable, Protocol, Tuple, Union, NamedTuple, Literal

T = TypeVar('T', bound=str, covariant=True)


class A(Protocol[T]):
    @property
    @abstractmethod
    def a(self) -> str: ...

    @property
    @abstractmethod
    def tag(self) -> T: ...


BType = A[Literal['B']]


class B(NamedTuple):
    a: str
    b: str
    tag: Literal['B'] = 'B'


class C(NamedTuple):
    a: str
    c: str

    tag: Literal['C'] = 'C'


def get_obj(stuff: A[T]) -> A[T]:
    return stuff


z: BType = get_obj(B('a', 'b'))
