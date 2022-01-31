from __future__ import annotations

from typing import NamedTuple, Tuple, FrozenSet, List, Optional, Literal, Dict

from mini_lisp.core import Symbols, Ast, parse, RawLeaves
from mini_lisp.core_types import Symbol, Variable, AstLeaf, AstNode, Number
from mini_lisp.program import FreeAst, Program, FreeAstLeaves
from mini_lisp.tree_utils import tree_replace, tree_parent_display


class PartialAst(NamedTuple):
    args: Tuple[AstNode[AstLeaf], ...]
    type: Literal["ast_parent"] = "ast_parent"

    @property
    def display(self):
        return tree_parent_display(self)

    def fill(self, symbols: Symbols) -> AstNode[RawLeaves]:
        return tree_replace(self, symbols.from_symbol, Symbol, Ast)

    def unfill(self, symbols: Symbols) -> AstNode[FreeAstLeaves]:
        return tree_replace(self, symbols.to_symbol, Variable, FreeAst)


class PartialProgram(NamedTuple):
    partial_ast: AstNode[AstLeaf]
    symbols: Symbols

    @property
    def display(self):
        return f"{self.partial_ast.display}\n, where {self.symbols}"

    def __repr__(self):
        return self.display

    @classmethod
    def from_program(cls, program: Program, keywords: FrozenSet[str]) -> PartialProgram:
        match_table = {k: v for k, v in program.symbols.from_symbol.items() if v in keywords}
        rest_table = {k: v for k, v in program.symbols.to_symbol.items() if k not in keywords}
        match_symbols = Symbols.from_from_symbol(match_table)
        rest_symbols = Symbols.from_to_symbol(rest_table)
        if isinstance(program.free_ast, Variable):
            # noinspection PyTypeChecker
            # cus Pycharm sucks
            return cls(Symbol(0), Symbols.from_from_symbol({Symbol(0): program.free_ast}))
        elif isinstance(program.free_ast, Number):
            return cls(program.free_ast, Symbols({}, {}))
        else:
            assert isinstance(program.free_ast, FreeAst)
            # noinspection PyTypeChecker
            # cus Pycharm sucks
            partial_ast_node = program.free_ast.fill(match_symbols, PartialAst)
            return cls(
                partial_ast=partial_ast_node,
                symbols=rest_symbols
            )

    @classmethod
    def from_ast(cls, ast: AstNode[RawLeaves]) -> PartialProgram:
        if isinstance(ast, Variable):
            if ast.name.startswith("?"):
                # noinspection PyTypeChecker
                # cus Pycharm sucks
                return cls(Symbol(0), Symbols.from_from_symbol({Symbol(0): ast}))
            else:
                return cls(ast, Symbols({}, {}))
        elif isinstance(ast, Number):
            return cls(ast, Symbols({}, {}))
        else:
            assert isinstance(ast, Ast)
            symbols = ast.get_symbols("?")
            print(f"symbols: {symbols}")
            partial_ast = ast.unfill(symbols, PartialAst)
            return cls(partial_ast, symbols)

    @classmethod
    def parse(cls, s: str) -> PartialProgram:
        return cls.from_ast(parse(s))


def match_node(tree_node: Ast, to_match: PartialAst) -> Optional[Symbols]:
    new_table: Dict[Symbol, AstNode[RawLeaves]] = {}
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
