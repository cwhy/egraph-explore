from __future__ import annotations

from typing import NamedTuple, Union, Tuple, Type, TypeVar

from mini_lisp.core import Symbols, Ast
from mini_lisp.core_types import Symbol
from mini_lisp.program import FreeAst
from mini_lisp.tree_utils import tree_display, tree_replace

T = TypeVar("T")


class PartialAst(NamedTuple):
    args: Tuple[Union[int, float, str, Symbol, PartialAst], ...]

    @property
    def display(self):
        return tree_display(self, PartialAst)

    def fill(self, symbols: Symbols) -> T:
        return tree_replace(self, symbols.from_symbol, Symbol, PartialAst, Ast)

    def unfill(self, symbols: Symbols) -> T:
        return tree_replace(self, symbols.to_symbol, str, PartialAst, FreeAst)


class PartialProgram(NamedTuple):
    partial_ast: PartialAst
    bound_table: BoundTable

    def __repr__(self):
        return f"{self.partial_ast}\n , where {self.bound_table}"

    @classmethod
    def from_program(cls, program: Program, keywords: FrozenSet[BoundedSymbol]) -> PartialProgram:
        match_table = {k: v for k, v in program.bound_table.bound.items() if v in keywords}
        to_free = {k: v for k, v in program.bound_table.free.items() if k not in keywords}
        to_bound = {k: v for k, v in program.bound_table.bound.items() if v not in keywords}
        return cls(
            partial_ast=get_ast_helper(program.free_ast, match_table, PartialAst),
            bound_table=BoundTable(to_free, to_bound)
        )

    @classmethod
    def from_ast(cls, ast: Ast) -> PartialProgram:
        to_free_table = extract_var_helper(ast, {}, "?")
        print(to_free_table, "tft, tft")
        partial_ast = map_symbols(ast, to_free_table, PartialAst)
        bound_table = BoundTable.from_free(to_free_table)
        return cls(partial_ast, bound_table)
