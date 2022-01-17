# %%
from __future__ import annotations

from typing import Literal, NamedTuple, Union, List

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2 a)"

ops = {"+", "-", "*", "/", "^"}
Op = str
Symbol = str


def tokenize(s: str) -> List[str]:
    return s.replace("(", " ( ").replace(")", " ) ").split()


class Ast(NamedTuple):
    op: Op
    args: List[Args]


Args = Union[int, float, Symbol, Ast]

example_tokens = tokenize(example)


def parse(tokens: List[str]) -> Args:
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
        assert op in ops
        for token in tokens[2:-1]:
            if token == "(":
