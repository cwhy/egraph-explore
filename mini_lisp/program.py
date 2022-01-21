from __future__ import annotations

from typing import NamedTuple, Union, Type, Tuple, TypeVar

from mini_lisp.core import Symbols, Ast, parse
from mini_lisp.core_types import Symbol, AstType, T
from mini_lisp.tree_utils import tree_display, tree_replace

TF = TypeVar("TF", bound=AstType)


class FreeAst(NamedTuple):
    args: Tuple[Union[int, float, Symbol, FreeAst], ...]

    @property
    def display(self):
        return tree_display(self, FreeAst)

    def fill(self, symbols: Symbols, target: Type[T]) -> T:
        return tree_replace(self, symbols.from_symbol, Symbol, FreeAst, target)


class Program(NamedTuple):
    free_ast: FreeAst
    symbols: Symbols

    @property
    def display_ast(self):
        return f"{self.free_ast.fill(self.symbols, Ast).display}\n , where {self.symbols}"

    @property
    def display(self):
        return f"{self.free_ast.display}\n , where {self.symbols}"

    def __repr__(self):
        return self.display

    @classmethod
    def from_ast(cls, ast: Ast) -> Program:
        symbols = ast.get_symbols()
        free_ast = ast.unfill(symbols, FreeAst)
        return cls(free_ast, symbols)

    @classmethod
    def parse(cls, s: str) -> Program:
        return cls.from_ast(parse(s))
