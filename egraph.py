from __future__ import annotations

from typing import NamedTuple, FrozenSet, Tuple, Union

from mini_lisp.core import parse
from mini_lisp.core_types import AstNode, Number, Symbol
from mini_lisp.program import Program, FreeAst, FreeAstLeaves
from mini_lisp.rules import Rule, parse_ruleset, RuleSet


class EGraph(NamedTuple):
    members: FrozenSet[FreeAstLeaves]
    children: Tuple[EGraph, ...]

    def display(self) -> str:
        members = ','.join(x.display for x in self.members)
        if len(self.children) > 0:
            children = f"{','.join([x.display() for x in self.children])}"
            if len(self.children) == 1:
                return f"[{members} -> {children}]"
            else:
                return f"[{members} -> ({children})]"
        else:
            return members

    @classmethod
    def from_free_ast(cls, free_ast: AstNode[FreeAstLeaves]) -> EGraph:
        if isinstance(free_ast, Number) or isinstance(free_ast, Symbol):
            return cls(frozenset({free_ast}), ())
        else:
            assert isinstance(free_ast, FreeAst)
            return cls(frozenset({free_ast.args[0]}), tuple(cls.from_free_ast(i) for i in free_ast.args[1:]))



example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2)"
parsed = parse(example)
all_symbols = parsed.get_symbols()
freed = parsed.unfill(all_symbols, FreeAst)
print(EGraph.from_free_ast(freed).display())

example2 = "(/ (* a 2) 2)"
ruleset = parse_ruleset(
    """
    (/ (* x y) z) == (* x (/ y z))
    (/ x x) == 1
    (* x 1) -> x
    (* x 2) == (<< x 1)
    (* x y) == (* y x)
    """
)

# print("\n".join(i.display for i in ruleset))
print("\n".join(i.short_display for i in ruleset))


def saturate(eg: EGraph, rule_set: RuleSet) -> EGraph:
    ...
