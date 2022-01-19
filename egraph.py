from __future__ import annotations
from typing import NamedTuple, Callable, List, Union, Literal, FrozenSet

from minilisp import Args, Ast, FreeAst, Symbol


class Rule(NamedTuple):
    to_lhs: FreeAst
    to_rhs: FreeAst


class EClass(NamedTuple):
    members: FrozenSet[EClass]


