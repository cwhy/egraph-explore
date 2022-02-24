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
    classes: Dict[int, Set[AstP]]
    registry: Dict[AstP, int]
    root_class: Optional[int] = None

    @property
    def root_nodes(self) -> Set[AstP]:
        if self.root_class is None:
            raise RuntimeError("Graph not initialized: Root class is not set")
        else:
            return self.classes[self.root_class]

    @property
    def n_classes(self) -> int:
        return len(self.classes)

    @property
    def next_class(self) -> int:
        return self.n_classes

    def attach_ast_node_(self, ast: AstP) -> None:
        if ast not in self.registry:
            self.registry[ast] = self.next_class
            self.classes[self.next_class] = {ast}

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
            # egraph.class_links[egraph.registry[ast]] = tuple(egraph.registry[a] for a in ast.args)

    @classmethod
    def from_ast(cls, ast: AstP) -> EGraph:
        egraph = cls(classes={}, registry={})
        EGraph.attach_ast_(ast, egraph)
        egraph.root_class = egraph.n_classes - 1
        return egraph

    def match_rule(self, rule: Rule) -> FrozenSet[RuleMatchResult]:
        return frozenset().union(*(rule.match_ast(n) for n in self.root_nodes))

    def merge_class_(self, from_class_id: int, to_class_id: int) -> None:
        to_class = self.classes.pop(to_class_id)
        self.classes[from_class_id] |= to_class
        if to_class == self.root_class:
            self.root_class = from_class_id
        for n in to_class:
            self.registry[n] = from_class_id

    def apply_(self, rule_match_result: RuleMatchResult) -> None:
        from_ast, to = rule_match_result
        from_class_id = self.registry[from_ast]
        if to not in self.registry:
            self.registry[to] = from_class_id
            self.classes[from_class_id].add(to)
            EGraph.attach_ast_(to, self)
        else:
            to_class_id = self.registry[to]
            self.merge_class_(from_class_id, to_class_id)

    def to_mermaid(self) -> MermaidGraph:
        print(self.registry)
        ## assume the dict is in order (python >= 3.6)
        node_ids: Dict[AstP, int] = {n: i for i, n in enumerate(self.registry.keys()) if n not in OPs}
        node_links = list((node_from_id, node_ids[node_to])
                          for node_from, node_from_id in node_ids.items()
                          if isinstance(node_from, AstParent)
                          for node_to in node_from.args[1:])

        style_gen = NodeStyle.get_style_gen()

        def style_format(node: AstNode[RawLeaves]) -> NodeStyle:
            if isinstance(node, AstParent):
                return style_gen(1)
            elif isinstance(node, Number):
                return style_gen(2)
            elif isinstance(node, Variable):
                if node in OPs:
                    raise RuntimeError("No OPs allowed here")
            return style_gen(4)

        subgraph_id, subgraph_content = list(zip(*filter(lambda x: len(x[-1]) > 0,
                                                         ((i, frozenset(node_ids[n] for n in v if n not in OPs))
                                                          for i, v in self.classes.items()))))
        return MermaidGraph(
            sub_graphs=subgraph_content,
            links=[(i, j) for i, j in node_links],
            sub_graph_links=[],
            subgraph_names=[f"\"{get_rounded_num(i)}\"" for i in subgraph_id],
            node_names={node_ids[k]: f"\"{k.display}\""
                        if not isinstance(k, AstParent)
                        else f"\"{k.args[0].display}\""
                        for k in self.registry.keys()
                        if k not in OPs},
            node_styles={node_ids[k]: style_format(k) for k in self.registry.keys() if k not in OPs},
        )

    def to_mermaid_org(self) -> MermaidGraph:
        ## assume the dict is in order (python >= 3.6)
        node_ids: Dict[AstP, int] = {n: i for i, n in enumerate(self.registry.keys())}
        node_links = list({(node_from_id, node_ids[node_to])
                           for node_from, node_from_id in node_ids.items()
                           if isinstance(node_from, AstParent)
                           for node_to in node_from.args})

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
            sub_graphs=[frozenset(node_ids[i] for i in s) for s in self.classes.values()],
            links=[(i, j) for i, j in node_links],
            sub_graph_links=[],
            subgraph_names=[f"\"{get_rounded_num(k)}\"" for k in self.classes.keys()],
            node_names={node_ids[k]: f"\"{k.display}\""
            if not isinstance(k, AstParent)
            else f"\"eval({MermaidGraph.node_fmt(node_ids[k])})\""
                        for k in self.registry.keys()},
            node_styles={node_ids[k]: style_format(k) for k in self.registry.keys()},
        )
