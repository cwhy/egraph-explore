from __future__ import annotations

from typing import TypeVar, Tuple, Union, NamedTuple, Dict, Optional, Type, List

from mini_lisp.core_types import Symbol
from mini_lisp.tree_utils import tree_replace, tree_display

T = TypeVar("T")


class Symbols(NamedTuple):
    to_symbol: Dict[Union[Ast, str], Symbol]
    from_symbol: Dict[Symbol, Union[str, Ast]]

    def __repr__(self):
        return " ┃ ".join(f"{s}: {i}" for i, s in self.to_symbol.items())

    @classmethod
    def from_to_symbol(cls, to_symbol_table: Dict[Union[Ast, str], Symbol]) -> Symbols:
        from_symbol_table = {}
        for key, value in to_symbol_table.items():
            from_symbol_table[value] = key
        return Symbols(to_symbol_table, from_symbol_table)

    @classmethod
    def from_from_symbol(cls, from_symbol_table: Dict[Symbol, Union[Ast, str]]) -> Symbols:
        to_symbol_table = {}
        for key, value in from_symbol_table.items():
            to_symbol_table[value] = key
        return Symbols(to_symbol_table, from_symbol_table)


class Ast(NamedTuple):
    args: Tuple[AstArgs, ...]

    @staticmethod
    def extract_var_helper(ast: Ast,
                           to_symbol_table: Dict[str, Symbol],
                           hole_prefix: Optional[str]) -> Dict[str, Symbol]:
        for arg in ast.args:
            if isinstance(arg, str):
                if hole_prefix is None or arg.startswith(hole_prefix):
                    to_symbol_table = {**to_symbol_table, **{arg: Symbol(len(to_symbol_table))}}
            elif isinstance(arg, Ast):
                to_symbol_table = Ast.extract_var_helper(arg, to_symbol_table, hole_prefix)
        return to_symbol_table

    def get_symbols(self, hole_prefix: Optional[str] = None) -> Symbols:
        return Symbols.from_to_symbol(Ast.extract_var_helper(self, {}, hole_prefix))

    def unfill(self, symbols: Symbols, target: Type[T]) -> T:
        return tree_replace(self, symbols.to_symbol, str, Ast, target)

    @property
    def display(self):
        return tree_display(self, Ast)


AstArgs = Union[int, float, str, Ast]


def tokenize(s: str) -> List[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


def parse_tokens(tokens: List[str]) -> AstArgs:
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
        i = 1
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
        return Ast(tuple(args))


def parse(s: str) -> AstArgs:
    return parse_tokens(tokenize(s))