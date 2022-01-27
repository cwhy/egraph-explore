from __future__ import annotations

from typing import NamedTuple, FrozenSet

from mini_lisp.rules import Rule


class EClass(NamedTuple):
    members: FrozenSet[EClass]


example = "(/ (* a 2) 2)"