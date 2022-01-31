from __future__ import annotations

from typing import NamedTuple, FrozenSet

from mini_lisp.rules import Rule, parse_ruleset


class EClass(NamedTuple):
    members: FrozenSet[EClass]


example = "(/ (* a 2) 2)"
ruleset = parse_ruleset(
    """
    (/ (* x y) z) == (* x (/ y z))
    (/ x x) == 1
    (* x 1) -> x
    (* x 2) == (<< x 1)
    (* x y) == (* y x)
    """
)

print("\n".join(i.short_display for i in ruleset))
# print("\n".join(i.display for i in ruleset))
