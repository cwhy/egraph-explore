from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Tuple, Union, NamedTuple, Optional, Type, List, Literal, Protocol, ItemsView, Generic

from mini_lisp.core_types import Symbol, AstLeaf, Number, Variable, AstNode, AstParent
from mini_lisp.tree_utils import tree_replace, tree_display, MyMapping, tree_parent_display

T = TypeVar("T", bound=AstLeaf)
TN = TypeVar("TN", bound=AstNode[AstLeaf])


@dataclass(frozen=True)
class Symbols(Generic[TN]):
    to_symbol: MyMapping[TN, Symbol]
    from_symbol: MyMapping[Symbol, TN]

    def __hash__(self) -> int:
        return hash(tuple(self.to_symbol.items()))

    def __repr__(self):
        return " ┃ ".join(f"{s.display}: {i.display}" for i, s in self.to_symbol.items())

    @classmethod
    def from_to_symbol(cls, to_symbol_table: MyMapping[TN, Symbol]) -> Symbols:
        from_symbol_table = {}
        for key, value in to_symbol_table.items():
            from_symbol_table[value] = key
        return Symbols(to_symbol_table, from_symbol_table)

    @classmethod
    def from_from_symbol(cls, from_symbol_table: MyMapping[Symbol, TN]) -> Symbols:
        to_symbol_table = {}
        for key, value in from_symbol_table.items():
            to_symbol_table[value] = key
        return Symbols(to_symbol_table, from_symbol_table)


class RawLeaves(Protocol):
    @property
    @abstractmethod
    def type(self) -> Literal["number", "variable"]: ...

    @property
    @abstractmethod
    def display(self) -> str: ...


def extract_var_helper(node: AstNode[RawLeaves],
                       to_symbol_table: MyMapping[AstLeaf, Symbol],
                       hole_prefix: Optional[str]) -> MyMapping[AstLeaf, Symbol]:
    if isinstance(node, Ast):
        for arg in node.args:
            to_symbol_table = extract_var_helper(arg, to_symbol_table, hole_prefix)
        return to_symbol_table
    elif isinstance(node, Variable):
        if hole_prefix is None or node.name.startswith(hole_prefix):
            return {**to_symbol_table, **{node: Symbol(len(to_symbol_table))}}
    else:
        assert isinstance(node, Number)
    return to_symbol_table


def get_symbols(node: AstNode[RawLeaves], hole_prefix: Optional[str] = None) -> Symbols[AstLeaf]:
    to_symbol = extract_var_helper(node, {}, hole_prefix)
    return Symbols.from_to_symbol(to_symbol)


class Ast(NamedTuple):
    args: Tuple[AstNode[RawLeaves], ...]
    type: Literal["ast_parent"] = "ast_parent"

    def get_symbols(self, hole_prefix: Optional[str] = None) -> Symbols[AstLeaf]:
        to_symbol = extract_var_helper(self, {}, hole_prefix)
        return Symbols.from_to_symbol(to_symbol)

    def unfill(self, symbols: Symbols, target: Type[AstParent[Union[T, Variable]]]) -> AstNode[Union[T, Variable]]:
        # noinspection PyTypeChecker
        # Because pycharm sucks
        return tree_replace(self, symbols.to_symbol, Variable, target)

    @property
    def display(self) -> str:
        return tree_parent_display(self)


def tokenize(s: str) -> List[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


def parse_tokens(tokens: List[str]) -> AstNode[RawLeaves]:
    if len(tokens) == 0:
        raise Exception("There must be something inside the parentheses")
    elif len(tokens) == 1:
        token = tokens[0]
        try:
            return Number.from_str(token)
        except ValueError:
            return Variable(token)
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


def parse(s: str) -> AstNode[RawLeaves]:
    return parse_tokens(tokenize(s))
