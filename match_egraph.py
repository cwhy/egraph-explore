from __future__ import annotations

from typing import Optional, FrozenSet

from egraph import EGraph, AstP
from mini_lisp.core import Symbols
from mini_lisp.core_types import Number, AstParent, Symbol
from mini_lisp.patterns import MatchResult
from mini_lisp.rules import Rule, RuleMatchResult


def match_rule(egraph: EGraph, rule: Rule) -> FrozenSet[RuleMatchResult]:
    return frozenset(filter(None, (match_node(egraph, node, rule) for node in egraph.registry)))


def match_node(graph: EGraph, node: AstP, rule: Rule) -> Optional[RuleMatchResult]:
    result = match_node_helper(graph, node, rule.lhs, Symbols.empty())
    return rule.apply(MatchResult(node, result)) if result is not None else None


def match_class_helper(graph: EGraph, class_id: int, to_match: AstP, session_symbols: Symbols) -> Optional[MatchResult]:
    # Only return the first one matched
    for node in graph.classes[class_id]:
        result = match_node_helper(graph, node, to_match, session_symbols)
        if result is not None:
            return MatchResult(node, result)
    else:
        return None


# Symbols: contains symbol <-> Ast information
# session_symbols: symbols that are matched and confirmed in the current match session
def match_node_helper(graph: EGraph, node: AstP, to_match: AstP, session_symbols: Symbols) -> Optional[Symbols]:
    if isinstance(to_match, AstParent):
        if not isinstance(node, AstParent):
            return None
        else:
            for arg1, arg2 in zip(node.args, to_match.args):
                assert arg1 in graph.registry
                result = match_class_helper(graph, graph.registry[arg1], arg2, session_symbols)
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
                if to_match in graph.registry:
                    assert node in graph.registry
                    if graph.registry[to_match] != graph.registry[node]:
                        return None
                    else:
                        return Symbols.empty()
                else:
                    return None
            else:
                return Symbols.empty()
