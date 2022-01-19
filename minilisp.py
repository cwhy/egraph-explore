# %%
from __future__ import annotations

from typing import Literal, NamedTuple, Union, List, Dict

BoundedSymbol = str


def tokenize(s: str) -> List[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


class Ast(NamedTuple):
    op: BoundedSymbol
    args: List[Args]


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


class FreeAst(NamedTuple):
    op: Symbol
    args: List[Args]


class SymbolTable(NamedTuple):
    free: Dict[BoundedSymbol, Symbol]
    bound: Dict[Symbol, BoundedSymbol]


def extract_var_helper(ast: Ast, free_table: Dict[BoundedSymbol, Symbol]) -> Dict[BoundedSymbol, Symbol]:
    if isinstance(ast, float) or isinstance(ast, int):
        return free_table
    elif isinstance(ast, BoundedSymbol):
        return {**free_table, **{ast: Symbol(len(free_table))}}
    else:
        free_table = {**free_table, **{ast.op: Symbol(len(free_table))}}
        for arg in ast.args:
            free_table = extract_var_helper(arg, free_table)
        return free_table

