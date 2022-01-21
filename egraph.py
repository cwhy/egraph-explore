from __future__ import annotations

from typing import NamedTuple, FrozenSet

from archive.minilisp import FreeAst


class Rule(NamedTuple):
    to_lhs: FreeAst
    to_rhs: FreeAst


class EClass(NamedTuple):
    members: FrozenSet[EClass]


