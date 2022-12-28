from __future__ import annotations

from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.rules import RuleSet, parse_ruleset, trim_ruleset


def saturate(egraph: EGraph, rule_set: RuleSet, visualize_lvl: int =0, max_iter: int = 200) -> None:
    iter_counter = 0
    h = hash(egraph)
    nh = None
    while nh != h:
        results = list(res for rule in rule_set for res in egraph.match_rule(rule))
        if len(results) == 0:
            break
        for result in results:
            old_h_in = hash(egraph)
            egraph.apply_(result)
            if hash(egraph) != old_h_in and visualize_lvl == 2:
                egraph.to_mermaid().view_()
        if hash(egraph) != old_h_in and visualize_lvl == 1:
            egraph.to_mermaid().view_()
        h = nh
        nh = hash(egraph)
        iter_counter += 1
        if iter_counter > max_iter:
            print("max_iter reached! ")
            break

def check_equality(ast, egraph):
    return ast in egraph.registry

example = "(* (+ a 2) b)"
g = EGraph.from_ast(parse(example))
g.to_mermaid().view_()

ruleset = parse_ruleset(
    """
    (* (+ x y) z) == (+ (* x z) (* y z))
    (* x y) == (* y x)
    """, trim=True
)
saturate(g, ruleset)
g.to_mermaid().view_()

# test equality
example2 = "(+ (* a b) (* 2 b))"
assert check_equality(parse(example2), g)