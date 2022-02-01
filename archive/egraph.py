from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple, FrozenSet, Tuple, Union, List, Dict, DefaultDict

from mini_lisp.core import parse
from mini_lisp.core_types import AstNode, Number, Symbol, AstParent
from mini_lisp.program import Program, FreeAst, FreeAstLeaves
from mini_lisp.rules import Rule, parse_ruleset, RuleSet


class EClass(NamedTuple):
    members: FrozenSet[FreeAstLeaves]

    def display(self) -> str:
        return '|'.join(x.display for x in self.members)

    @classmethod
    def from_astleaf(cls, astleaf: FreeAstLeaves) -> EClass:
        return cls(frozenset([astleaf]))


class EGraph(NamedTuple):
    root: EClass
    edges: Dict[EClass, List[EClass]]

    def display(self) -> str:
        edge_str = '\n'.join(
            f"{k.display()} -> {'|'.join(v.display() for v in vs)}"
            for k, vs in self.edges.items())
        return str(self.root.display()) + '\n' + edge_str

    @classmethod
    def from_free_ast(cls, free_ast: AstNode[FreeAstLeaves]) -> EGraph:
        edges: DefaultDict[EClass, List[EClass]] = defaultdict(list)
        bfs = [free_ast]
        while bfs:
            current = bfs.pop(0)
            if isinstance(current, AstParent):
                op = current.args[0]
                for arg in current.args[1:]:
                    bfs.append(arg)
                    edges[EClass.from_astleaf(op)].append(EClass.from_astleaf(arg))
        root = EClass.from_astleaf(free_ast.args[0])
        return EGraph(root, dict(edges))


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


def add_rule(eg: EGraph, rule: Rule) -> EGraph:
    ...
