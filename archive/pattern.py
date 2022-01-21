from __future__ import annotations
from typing import Optional, NamedTuple, Union, List, FrozenSet, Iterable

from display import display_ast_helper
from minilisp import BoundTable, FreeAst, Ast, BoundedSymbol, Symbol, Program, get_ast_helper, parse, \
    extract_var_helper, map_symbols


class PartialAst(NamedTuple):
    op: Union[BoundedSymbol, Symbol]
    args: List[Args]

    def __repr__(self):
        return repr(self.op) + "\n" + "\n".join(display_ast_helper(self, ''))


Args = Union[int, float, BoundedSymbol, PartialAst]


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


def parse2partial(s: str, keywords: Iterable[BoundedSymbol]) -> PartialProgram:
    return PartialProgram.from_program(parse(s).decoupled, frozenset(keywords))


def parse_partial(s: str) -> PartialProgram:
    return PartialProgram.from_ast(parse(s))


def match(ast: Ast, to_match: PartialAst) -> Optional[BoundTable]:
    op_match = False
    if ast.op != to_match.op:
        # TODO logic is still wrong here
        return None
    else:
        new_table = {}
        for arg1, arg2 in zip(ast.args, to_match.args):
            if isinstance(arg2, PartialAst):
                if not isinstance(arg1, Ast):
                    return None
                else:
                    return match(arg1, arg2)
            elif not isinstance(arg2, Symbol):
                if arg1 != arg2:
                    return None
            else:
                if arg2 in new_table:
                    if new_table[arg2] != arg1:
                        return None
                else:
                    new_table[arg2] = arg1
        return BoundTable.from_bound(new_table)
