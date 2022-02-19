from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple, FrozenSet, Tuple, Union, List, Dict, DefaultDict, Set

from mini_lisp.core import parse, RawLeaves, Symbols
from mini_lisp.core_types import AstNode, Number, Symbol, AstParent, Variable
from mini_lisp.patterns import match
from mini_lisp.program import Program, FreeAst, FreeAstLeaves
from mini_lisp.rules import Rule, parse_ruleset, RuleSet, RuleMatchResult

AstP = AstNode[RawLeaves]


class EGraph(NamedTuple):
    class_links: Dict[int, Tuple[int, ...]]
    classes: List[Set[AstP]]
    registry: Dict[AstP, int]

    @property
    def root_node(self):
        return next(iter(self.classes[-1]))

    @staticmethod
    def from_ast_helper_(ast: AstP, egraph: EGraph) -> None:
        if isinstance(ast, Number) or isinstance(ast, Variable):
            if ast not in egraph.registry:
                egraph.classes.append({ast})
                egraph.registry[ast] = len(egraph.classes) - 1
        else:
            assert isinstance(ast, AstParent)
            for arg in ast.args:
                EGraph.from_ast_helper_(arg, egraph)
            egraph.classes.append({ast})
            cls_id = len(egraph.classes) - 1
            egraph.registry[ast] = cls_id
            egraph.class_links[cls_id] = tuple(egraph.registry[a] for a in ast.args)

    @classmethod
    def from_ast(cls, ast: AstP) -> EGraph:
        egraph = cls(class_links={}, classes=[], registry={})
        EGraph.from_ast_helper_(ast, egraph)
        return egraph

    def match_rule(self, rule: Rule) -> FrozenSet[RuleMatchResult]:
        return rule.match(self.root_node)

    def apply_(self, rule_match_result: RuleMatchResult) -> None:
        index, to = rule_match_result
        class_id = self.registry[index]
        self.registry[to] = class_id
        self.classes[class_id].add(to)

    def to_mermaid(self) -> str:
