# %%
from __future__ import annotations

from typing import NamedTuple, Union, List, Dict, Protocol, TypeVar, Type, Optional

from display import display_ast_helper

BoundedSymbol = str

T = TypeVar("T")


def tokenize(s: str) -> List[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


def extract_var_helper(ast: Ast, free_table: Dict[BoundedSymbol, Symbol],
                       hole_prefix: Optional[str] = None) -> Dict[BoundedSymbol, Symbol]:
    if isinstance(ast, float) or isinstance(ast, int):
        return free_table
    elif isinstance(ast, BoundedSymbol):
        if hole_prefix is None or ast.startswith(hole_prefix):
            return {**free_table, **{ast: Symbol(len(free_table))}}
        else:
            return free_table
    else:
        if hole_prefix is None or ast.op.startswith(hole_prefix):
            free_table = {**free_table, **{ast.op: Symbol(len(free_table))}}
        for arg in ast.args:
            free_table = extract_var_helper(arg, free_table, hole_prefix)
        return free_table


class Ast(NamedTuple):
    op: BoundedSymbol
    args: List[Args]

    def __repr__(self):
        return repr(self.op) + "\n" + "\n".join(display_ast_helper(self, ''))

    @property
    def decoupled(self) -> Program:
        to_free_table = extract_var_helper(self, {})
        bound_table = BoundTable.from_free(to_free_table)
        return Program(map_symbols(self, to_free_table, FreeAst), bound_table)


def map_symbols(ast: Ast, free_table: Dict[BoundedSymbol, Symbol], ast_type: Type[T]) -> T:
    free_args = []
    for arg in ast.args:
        if isinstance(arg, int) or isinstance(arg, float):
            free_args.append(arg)
        elif isinstance(arg, BoundedSymbol):
            # if arg is not in free_table, just return it
            free_args.append(free_table.get(arg, arg))
        else:
            assert isinstance(arg, Ast)
            free_args.append(map_symbols(arg, free_table, ast_type))
    # if op is not in free_table, just return it
    return ast_type(free_table.get(ast.op, ast.op), free_args)


Args = Union[int, float, BoundedSymbol, Ast]


def parse_tokens(tokens: List[str]) -> Args:
    if len(tokens) == 0:
        raise Exception("There must be something inside the parentheses")
    elif len(tokens) == 1:
        token = tokens[0]
        try:
            return float(token)
        except ValueError:
            return token
    else:
        assert len(tokens) >= 4
        assert tokens[0] == "("
        assert tokens[-1] == ")"
        op = tokens[1]
        assert isinstance(op, str)
        args = []
        i = 2
        while i < len(tokens) - 1:
            token = tokens[i]
            if token == "(":
                bracket_stack = 1
                j = i
                while True:
                    if tokens[j] == ")":
                        bracket_stack -= 1
                        if bracket_stack == 1:
                            break
                    elif tokens[j] == "(":
                        bracket_stack += 1
                    j += 1
                args.append(parse_tokens(tokens[i:j + 1]))
                i = j + 1
            else:
                args.append(parse_tokens([token]))
                i += 1
        return Ast(op, args)


def parse(s: str) -> Args:
    return parse_tokens(tokenize(s))


class Symbol(NamedTuple):
    index: int

    def __repr__(self):
        return f"\\{self.index}"

    def __str__(self):
        return f"\\{self.index}"


class BoundTable(NamedTuple):
    free: Dict[Union[Ast, BoundedSymbol], Symbol]
    bound: Dict[Symbol, Union[BoundedSymbol, Ast]]

    def __repr__(self):
        return ", ".join(f"{s} = ({i})" for i, s in self.free.items())

    @classmethod
    def from_free(cls, to_free_table: Dict[Union[Ast, BoundedSymbol], Symbol]) -> BoundTable:
        to_bound_table = {}
        for key, value in to_free_table.items():
            to_bound_table[value] = key
        return BoundTable(to_free_table, to_bound_table)

    @classmethod
    def from_bound(cls, to_bound_table: Dict[Symbol, Union[Ast, BoundedSymbol]]) -> BoundTable:
        to_free_table = {}
        for key, value in to_bound_table.items():
            to_free_table[value] = key
        return BoundTable(to_free_table, to_bound_table)


class FreeAst(NamedTuple):
    op: Symbol
    args: List[Args]

    def __repr__(self):
        return repr(self.op) + "\n" + "\n".join(display_ast_helper(self, ''))


def get_ast_helper(free_ast: FreeAst,
                   to_bound_table: Dict[Symbol, Union[BoundedSymbol, Ast]], ast_type: Type[T]) -> T:
    args = []
    for arg in free_ast.args:
        if isinstance(arg, Symbol):
            # if arg is not in to_bound_table, just return it
            args.append(to_bound_table.get(arg, arg))
        elif isinstance(arg, FreeAst):
            args.append(get_ast_helper(arg, to_bound_table, ast_type))
        else:
            args.append(arg)
    return ast_type(to_bound_table[free_ast.op], args)


class Program(NamedTuple):
    free_ast: FreeAst
    bound_table: BoundTable

    def __repr__(self):
        return f"{self.free_ast}\n , where {self.bound_table}"

    @property
    def ast(self) -> Ast:
        return get_ast_helper(self.free_ast, self.bound_table.bound, Ast)
