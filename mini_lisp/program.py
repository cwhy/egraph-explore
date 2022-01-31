from __future__ import annotations

from abc import abstractmethod
from typing import NamedTuple, Type, Tuple, Literal, Protocol, Union, TypeVar

from mini_lisp.core import Symbols, Ast, parse, RawLeaves
from mini_lisp.core_types import Symbol, AstNode, Variable, Number, AstParent, AstLeaf
from mini_lisp.tree_utils import tree_display, tree_replace, tree_parent_display


class FreeAstLeaves(Protocol):
    @property
    @abstractmethod
    def type(self) -> Literal["number", "symbol"]: ...

    @property
    @abstractmethod
    def display(self) -> str: ...


T = TypeVar("T", bound=AstLeaf)


class FreeAst(NamedTuple):
    args: Tuple[AstNode[FreeAstLeaves], ...]
    type: Literal["ast_parent"] = "ast_parent"

    @property
    def display(self) -> str:
        return tree_parent_display(self)

    def fill(self, symbols: Symbols, target: Type[AstParent[Union[T, Symbol]]]) -> AstNode[Union[T, Symbol]]:
        return tree_replace(self, symbols.from_symbol, Symbol, target)


class Program(NamedTuple):
    free_ast: AstNode[FreeAstLeaves]
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
    def from_ast(cls, ast: AstNode[RawLeaves]) -> Program:
        if isinstance(ast, Variable):
            # noinspection PyTypeChecker
            # cus Pycharm sucks
            return cls(Symbol(0), Symbols.from_from_symbol({Symbol(0): ast}))
        elif isinstance(ast, Number):
            return cls(ast, Symbols({}, {}))
        else:
            assert isinstance(ast, Ast)
            symbols = ast.get_symbols()
            # noinspection PyTypeChecker
            # cus Pycharm sucks
            # can't use ast.unfill here cus mypy sucks
            free_ast = tree_replace(ast, symbols.to_symbol, Variable, FreeAst)
            return cls(free_ast, symbols)

    @classmethod
    def parse(cls, s: str) -> Program:
        return cls.from_ast(parse(s))
