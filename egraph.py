from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set, Optional

from graph_visualization import MermaidGraph, NodeStyle, Linkable, Link, LinkableType
from mini_lisp.core import RawLeaves
from mini_lisp.core_types import AstNode, Number, AstParent, Variable
from mini_lisp.rules import RuleMatchResult, OPs
from utils.misc import get_rounded_num

AstP = AstNode[RawLeaves]


@dataclass
class EGraph:
    # classes are represented by ID, which nodes are represented by AST
    # classes: id -> set of nodes in a class
    # registry: nodes belongs to which classes
    classes: Dict[int, Set[AstP]]
    registry: Dict[AstP, int]
    root_class: Optional[int] = None

    def __hash__(self):
        return hash(tuple((k, hash(frozenset(v))) for k, v in self.classes.items()))

    @property
    def root_nodes(self) -> Set[AstP]:
        if self.root_class is None:
            raise RuntimeError("Graph not initialized: Root class is not set")
        else:
            return self.classes[self.root_class].copy()

    def attach_ast_node_(self, ast: AstP) -> None:
        if ast not in self.registry:
            # TODO this is not efficient
            new_class_id = max(self.classes.keys(), default=0) + 1
            self.registry[ast] = new_class_id
            self.classes[new_class_id] = {ast}

    @staticmethod
    def attach_ast_(ast: AstP, egraph: EGraph) -> None:
        if isinstance(ast, Number) or isinstance(ast, Variable):
            egraph.attach_ast_node_(ast)
        else:
            if not isinstance(ast, AstParent):
                raise Exception(f"Ast {ast} has unexpected type: {type(ast)}")
            for arg in ast.args:
                EGraph.attach_ast_(arg, egraph)
            egraph.attach_ast_node_(ast)
            # egraph.class_links[egraph.registry[ast]] = tuple(egraph.registry[a] for a in ast.args)

    @classmethod
    def from_ast(cls, ast: AstP) -> EGraph:
        egraph = cls(classes={}, registry={})
        EGraph.attach_ast_(ast, egraph)
        egraph.root_class = len(egraph.classes)
        return egraph

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
        assert from_class_id in self.classes
        if to not in self.registry:
            self.registry[to] = from_class_id
            self.classes[from_class_id].add(to)
            EGraph.attach_ast_(to, self)
        else:
            to_class_id = self.registry[to]
            if from_class_id != to_class_id:
                self.merge_class_(from_class_id, to_class_id)

    def to_mermaid(self) -> MermaidGraph:
        ## assume the dict is in order (python >= 3.6)
        node_ids: Dict[AstP, int] = {n: i for i, n in enumerate(self.registry.keys()) if n not in OPs}

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

        subgraph_eclass_id, subgraph_content = list(zip(*filter(lambda x: len(x[-1]) > 0,
                                                                ((i, frozenset(node_ids[n] for n in v if n not in OPs))
                                                                 for i, v in self.classes.items()))))
        subgraph_eclass_id_to_idx = {v: i for i, v in enumerate(subgraph_eclass_id)}

        def make_link(i: int, j: int, arg_n: int) -> Link:
            return Link(Linkable(i, LinkableType.Node), Linkable(j, LinkableType.Subgraph), content=f"{arg_n}")

        links = list(make_link(node_from_id, subgraph_eclass_id_to_idx[self.registry[node_to]], arg_n)
                     for node_from, node_from_id in node_ids.items()
                     if isinstance(node_from, AstParent)
                     for arg_n, node_to in enumerate(node_from.args[1:]))

        return MermaidGraph(
            sub_graphs=subgraph_content,
            links=links,
            subgraph_names=[f"\"{get_rounded_num(i)}\"" for i in subgraph_eclass_id],
            node_names={node_ids[k]: f"{k.display}"
            if not isinstance(k, AstParent)
            else f"{k.args[0].display}"
                        for k in self.registry.keys()
                        if k not in OPs},
            node_styles={node_ids[k]: style_format(k) for k in self.registry.keys() if k not in OPs},
        )
