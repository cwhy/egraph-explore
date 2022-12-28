from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import NamedTuple, FrozenSet, Tuple, List, Dict, Set, Optional

from mini_lisp.core import RawLeaves, Symbols
from mini_lisp.core_types import AstNode, Number, AstParent, Variable, Symbol
from mini_lisp.patterns import MatchResult
from mini_lisp.rules import Rule, RuleMatchResult, OPs
from graph_visualization import MermaidGraph, NodeStyle
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
            return self.classes[self.root_class]

    def attach_ast_node_(self, ast: AstP) -> None:
        # TODO this is not efficient
        new_class_id = max(self.classes.keys(), default=0) + 1
        if ast not in self.registry:
            self.registry[ast] = new_class_id
            self.classes[new_class_id] = {ast}

    @staticmethod
    def attach_ast_(ast: AstP, egraph: EGraph) -> None:
        if isinstance(ast, Number) or isinstance(ast, Variable):
            egraph.attach_ast_node_(ast)
        else:
            if not isinstance(ast, AstParent):
                raise Exception(f"Ast {ast} has unknown type: {type(ast)}")
            for arg in ast.args:
                EGraph.attach_ast_(arg, egraph)
            egraph.attach_ast_node_(ast)
            # egraph.class_links[egraph.registry[ast]] = tuple(egraph.registry[a] for a in ast.args)

    @classmethod
    def from_ast(cls, ast: AstP) -> EGraph:
        egraph = cls(classes={}, registry={})
        EGraph.attach_ast_(ast, egraph)
        egraph.root_class = len(egraph.classes) - 1
        return egraph

    def match_class_helper(self, class_id: int, to_match: AstP, session_symbols: Symbols) -> Optional[MatchResult]:
        # Only return the first one matched
        for node in self.classes[class_id]:
            result = self.match_node_helper(node, to_match, session_symbols)
            if result is not None:
                return MatchResult(node, result)
        else:
            return None

    # Symbols: contains symbol <-> Ast information
    # session_symbols: symbols that are matched and confirmed in the current match session
    def match_node_helper(self, node: AstP, to_match: AstP, session_symbols: Symbols) -> Optional[Symbols]:
        if isinstance(to_match, AstParent):
            if not isinstance(node, AstParent):
                return None
            else:
                for arg1, arg2 in zip(node.args, to_match.args):
                    assert arg1 in self.registry
                    result = self.match_class_helper(self.registry[arg1], arg2, session_symbols)
                    if result is not None:
                        session_symbols |= result.symbols
                    else:
                        return None
                else:
                    return session_symbols
        else:
            if isinstance(to_match, Symbol):
                # symbol is not there or has same value
                if node == session_symbols.from_symbol.get(to_match, node):
                    return Symbols.from_from_symbol({to_match: node})
                else:
                    return None
            elif isinstance(node, AstParent):
                return None
            elif isinstance(node, Number) and isinstance(to_match, Symbol):
                return Symbols.from_from_symbol({to_match: node})
            else:
                if to_match != node:
                    if to_match in self.registry:
                        assert node in self.registry
                        if self.registry[to_match] != self.registry[node]:
                            return None
                        else:
                            return Symbols.empty()
                    else:
                        return None
                else:
                    return Symbols.empty()

    def match_node(self, node: AstP, rule: Rule) -> Optional[RuleMatchResult]:
        result = self.match_node_helper(node, rule.lhs, Symbols.empty())
        return rule.apply(MatchResult(node, result)) if result is not None else None

    def match_rule(self, rule: Rule) -> FrozenSet[RuleMatchResult]:
        return frozenset(filter(None, (self.match_node(node, rule) for node in self.registry)))

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
