from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple, FrozenSet, Tuple, Union, List, Dict, DefaultDict

from mini_lisp.core import parse, RawLeaves
from mini_lisp.core_types import AstNode, Number, Symbol, AstParent, Variable
from mini_lisp.program import Program, FreeAst, FreeAstLeaves
from mini_lisp.rules import Rule, parse_ruleset, RuleSet

AstP = AstNode[RawLeaves]


class EGraph(NamedTuple):
    class_links: Dict[int, Tuple[int, ...]]
    classes: List[FrozenSet[AstP]]
    registry: Dict[AstP, int]

    @staticmethod
    def from_ast_helper_(ast: AstNode[AstP], egraph: EGraph) -> None:
        if isinstance(ast, Number) or isinstance(ast, Variable):
            if ast not in egraph.registry:
                egraph.classes.append(frozenset([ast]))
                egraph.registry[ast] = len(egraph.classes) - 1
        else:
            assert isinstance(ast, AstParent)
            for arg in ast.args:
                EGraph.from_ast_helper_(arg, egraph)
            egraph.classes.append(frozenset([ast]))
            cls_id = len(egraph.classes) - 1
            egraph.registry[ast] = cls_id
            egraph.class_links[cls_id] = tuple(egraph.registry[a] for a in ast.args)

    @classmethod
    def from_ast(cls, ast: AstNode[AstP]) -> EGraph:
        egraph = cls(class_links={}, classes=[], registry={})
        EGraph.from_ast_helper_(ast, egraph)
        return egraph

    def match_rule_(self, rule: Rule) -> List[Tuple[AstP, Symbol]]:
