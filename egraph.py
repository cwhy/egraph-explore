from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import NamedTuple, FrozenSet, Tuple, List, Dict, Set, Optional

from mini_lisp.core import RawLeaves
from mini_lisp.core_types import AstNode, Number, AstParent, Variable
from mini_lisp.rules import Rule, RuleMatchResult, OPs
from graph_visualization import MermaidGraph, NodeStyle
from utils.misc import get_rounded_num

AstP = AstNode[RawLeaves]


@dataclass
class EGraph:
    class_links: Dict[int, Tuple[int, ...]]
    classes: List[Set[AstP]]
    registry: Dict[AstP, int]
    root_class: Optional[int] = None

    @property
    def root_nodes(self) -> Set[AstP]:
        if self.root_class is None:
            raise RuntimeError("Graph not initialized: Root class is not set")
        else:
            return self.classes[self.root_class]

    def attach_ast_node_(self, ast: AstP) -> None:
        if ast not in self.registry:
            self.classes.append({ast})
            self.registry[ast] = len(self.classes) - 1

    @staticmethod
    def attach_ast_(ast: AstP, egraph: EGraph) -> None:
        if isinstance(ast, Number) or isinstance(ast, Variable):
            egraph.attach_ast_node_(ast)
        else:
            if not isinstance(ast, AstParent):
                print(ast)
            assert isinstance(ast, AstParent)
            for arg in ast.args:
                EGraph.attach_ast_(arg, egraph)
            egraph.attach_ast_node_(ast)
            egraph.class_links[egraph.registry[ast]] = tuple(egraph.registry[a] for a in ast.args)

    @classmethod
    def from_ast(cls, ast: AstP) -> EGraph:
        egraph = cls(class_links={}, classes=[], registry={})
        EGraph.attach_ast_(ast, egraph)
        egraph.root_class = len(egraph.classes) - 1
        return egraph

    def match_rule(self, rule: Rule) -> FrozenSet[RuleMatchResult]:
        return frozenset().union(*(rule.match(n) for n in self.root_nodes))

    def apply_(self, rule_match_result: RuleMatchResult) -> None:
        index, to = rule_match_result
        class_id = self.registry[index]
        self.registry[to] = class_id
        self.classes[class_id].add(to)
        EGraph.attach_ast_(to, self)

    def to_mermaid(self) -> MermaidGraph:
        print(self.registry)
        ## assume the dict is in order (python >= 3.6)
        node_ids: Dict[AstP, int] = {n: i for i, n in enumerate(self.registry.keys())}
        node_links = list({(node_from_id, node_ids[node_to])
                           for node_from, node_from_id in node_ids.items()
                           if isinstance(node_from, AstParent)
                           for node_to in node_from.args})

        """
        Node links from class links
        node_links = list({(node_from_id, node_ids[node_to])
                           for node_from, node_from_id in node_ids.items()
                           for class_to in self.class_links.get(self.registry[node_from], ())
                           for node_to in self.classes[class_to]
                           if isinstance(node_from, AstParent)})
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

        style_gen = NodeStyle.get_style_gen()

        def style_format(node: AstNode[RawLeaves]) -> NodeStyle:
            if isinstance(node, AstParent):
                return style_gen(0)
            elif isinstance(node, Number):
                return style_gen(2)
            elif isinstance(node, Variable):
                if node in OPs:
                    return style_gen(1)
            return style_gen(4)

        return MermaidGraph(
            sub_graphs=[frozenset(node_ids[i] for i in s) for s in self.classes],
            links=[(i, j) for i, j in node_links],
            sub_graph_links=[],
            subgraph_names=[f"\"{get_rounded_num(i)}\"" for i in range(len(self.classes))],
            node_names={node_ids[k]: f"\"{k.display}\""
                        if not isinstance(k, AstParent)
                        else f"\"eval({MermaidGraph.node_fmt(node_ids[k])})\""
                        for k in self.registry.keys()},
            node_styles={node_ids[k]: style_format(k) for k in self.registry.keys()},
        )
