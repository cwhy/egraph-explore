from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple, FrozenSet, Tuple, Union, List, Dict, DefaultDict

from mini_lisp.core import parse
from mini_lisp.core_types import AstNode, Number, Symbol, AstParent
from mini_lisp.program import Program, FreeAst, FreeAstLeaves
from mini_lisp.rules import Rule, parse_ruleset, RuleSet


class EGraph(NamedTuple):
    root: FreeAstLeaves
    node_link: Dict[FreeAstLeaves, FreeAstLeaves]
    classes: List[FrozenSet[FreeAstLeaves]]
    # Must use at least Python 3.7 to preserve the dict order
    node2class: Dict[FreeAstLeaves, int]

    def add_new_(self, node: FreeAstLeaves, parent: FreeAstLeaves):
        assert parent in self.node2class
        assert node not in self.node2class
        self.node2class[node] = len(self.classes)
        self.classes.append(frozenset([node]))
        self.node_link[parent] = node

    def add_link_(self, node: FreeAstLeaves, parent: FreeAstLeaves):
        assert node in self.node2class
        assert parent in self.node2class
        self.node_link[parent] = node

    @classmethod
    def from_free_ast(cls, free_ast: AstNode[FreeAstLeaves]) -> EGraph:
        empty = cls(free_ast, {}, [], {})
        bfs = [free_ast]
        while bfs:
            current = bfs.pop(0)
            if isinstance(current, AstParent):
                op = current.args[0]

                for arg in current.args[1:]:
                    bfs.append(arg)

                    if isinstance(arg, FreeAstLeaves):
                        if arg not in empty.node2class:
                            empty.add_new_(arg, op)
                        else:
                            assert arg in empty.node2class
                            empty.add_link_(arg, op)
                    else:
                        assert isinstance(arg, AstParent)
                        if arg. not in empty.node_link:

                    empty.add_new_(op, current.parent)


        root = EClass.from_astleaf(free_ast.args[0])
        return EGraph(root, dict(edges))
