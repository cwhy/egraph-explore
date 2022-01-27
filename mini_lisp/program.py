from __future__ import annotations

from typing import NamedTuple, Type, Tuple, Literal, Protocol

from mini_lisp.core import Symbols, Ast, parse, AstArgs
from mini_lisp.core_types import Symbol, T, AstNode, Variable, Float
from mini_lisp.tree_utils import tree_display, tree_replace

FreeAstNodeType = Literal["ast", "float", "symbol"]


class FreeAstArgs(Protocol):
    type: Literal["float", "symbol"]


class FreeAst(NamedTuple):
    args: Tuple[FreeAstArgs, ...]
    type: Literal["ast_parent"] = "ast_parent"

    @property
    def display(self):
        return tree_display(self, FreeAst)

    def fill(self, symbols: Symbols, target: Type[AstNode[T]]) -> AstNode[T]:
        return tree_replace(self, symbols.from_symbol, Symbol, target)


class Program(NamedTuple):
    free_ast: AstNode[FreeAstArgs]
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
    def from_ast(cls, ast: AstNode[AstArgs]) -> Program:
        if isinstance(ast, Variable):
            return cls(Symbol(0), Symbols.from_from_symbol({Symbol(0): ast}))
        elif isinstance(ast, Float):
            return cls(ast, Symbols({}, {}))
        else:
            assert isinstance(ast, Ast)
            symbols = ast.get_symbols()
            free_ast = ast.unfill(symbols, FreeAst)
            return cls(free_ast, symbols)

    @classmethod
    def parse(cls, s: str) -> Program:
        return cls.from_ast(parse(s))
