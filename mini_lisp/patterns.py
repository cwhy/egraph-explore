from __future__ import annotations

from typing import NamedTuple, Union, Tuple, Type, TypeVar, FrozenSet, List, Optional

from mini_lisp.core import Symbols, Ast, parse
from mini_lisp.core_types import Symbol
from mini_lisp.program import FreeAst, Program
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
    symbols: Symbols

    @property
    def display(self):
        return f"{self.partial_ast.display}\n , where {self.symbols}"

    def __repr__(self):
        return self.display

    @classmethod
    def from_program(cls, program: Program, keywords: FrozenSet[str]) -> PartialProgram:
        match_table = {k: v for k, v in program.symbols.from_symbol.items() if v in keywords}
        rest_table = {k: v for k, v in program.symbols.to_symbol.items() if k not in keywords}
        match_symbols = Symbols.from_from_symbol(match_table)
        rest_symbols = Symbols.from_to_symbol(rest_table)
        return cls(
            partial_ast=program.free_ast.fill(match_symbols, PartialAst),
            symbols=rest_symbols
        )

    @classmethod
    def from_ast(cls, ast: Ast) -> PartialProgram:
        symbols = ast.get_symbols("?")
        print(f"symbols: {symbols}")
        partial_ast = ast.unfill(symbols, PartialAst)
        return cls(partial_ast, symbols)

    @classmethod
    def parse(cls, s: str) -> PartialProgram:
        return cls.from_ast(parse(s))


def match_node(tree_node: Ast, to_match: PartialAst) -> Optional[Symbols]:
    new_table = {}
    for arg1, arg2 in zip(tree_node.args, to_match.args):
        if isinstance(arg2, PartialAst):
            if not isinstance(arg1, Ast):
                return None
            else:
                return match_node(arg1, arg2)
        elif not isinstance(arg2, Symbol):
            if arg1 != arg2:
                return None
        else:
            if arg2 in new_table:
                if new_table[arg2] != arg1:
                    return None
            else:
                new_table[arg2] = arg1
    return Symbols.from_from_symbol(new_table)


def match(ast: Ast, to_match: PartialAst) -> List[Symbols]:
    sym_list = []
    res = match_node(ast, to_match)
    if res is not None:
        sym_list.append(res)
    for arg1 in ast.args:
        if isinstance(arg1, Ast):
            sym_list += match(arg1, to_match)
    return sym_list

