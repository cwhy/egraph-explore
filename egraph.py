from __future__ import annotations

from typing import NamedTuple, FrozenSet, Tuple, List, Dict, Set

from mini_lisp.core import RawLeaves
from mini_lisp.core_types import AstNode, Number, AstParent, Variable
from mini_lisp.rules import Rule, RuleMatchResult
from graph_visualization import MermaidGraph, hex2str, color_pair_gen

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

    def to_mermaid(self) -> MermaidGraph:
        print(self.registry)
        ## assume the dict is in order (python >= 3.6)
        node_ids: Dict[AstP, int] = {n: i for i, n in enumerate(self.registry.keys())}
        node_links = list({(node_from_id, node_ids[node_to])
                           for node_from, node_from_id in node_ids.items()
                           for class_to in self.class_links.get(self.registry[node_from], ())
                           for node_to in self.classes[class_to]
                           if isinstance(node_from, AstParent)})

        """
        More readable version of the previous code:
        node_links = set()
        for node_from, node_from_id in node_ids.items():
            if isinstance(node_from, AstParent):
                class_from = self.registry[node_from]
                class_to = self.class_links.get(class_from, ())
                for j in class_to:
                    for node_to in self.classes[j]:
                        node_links.add((node_from_id, node_ids[node_to]))
        """

        n_class_ids = len(self.registry)
        styles = (n_class_ids)

        def get_style(node_id: int) -> str:
            f, s = colors[node_id]
            return f"fill:{hex2str(f)},stroke:{hex2str(s)},stroke-width:4px"

        return MermaidGraph.init_all_subgraph(
            sub_graphs=[frozenset(x.display if not isinstance(x, AstParent) else "") for x in self.registry.keys()],
            links=[],
            sub_graph_links=node_links,
            node_names=[f"EClass{self.registry[x]}" for x in self.registry.keys()],
            node_styles={i: get_style(i) for i in range(n_class_ids)},
        )
