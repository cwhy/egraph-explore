from __future__ import annotations

from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.rules import RuleSet, parse_ruleset, trim_ruleset


def all_match_(egraph: EGraph, rule_set: RuleSet, max_iter: int = 200) -> None:
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
            if hash(egraph) != old_h_in:
                egraph.to_mermaid().view_()
        h = nh
        nh = hash(egraph)
        iter_counter += 1
        if iter_counter > 100:
            break


example = "(/ (^ (* (+ (* 0 3) 2 3) x 4) (- 2)) (- 2))"
egraph = EGraph.from_ast(parse(example))
egraph.to_mermaid().view_()
ruleset = parse_ruleset(
    """
    (/ (* x y) z) == (* x (/ y z))
    (/ x x) == 1
    (* x 1) -> x
    (* x 2) == (<< x 1)
    (* x y) == (* y x)
    """, trim=True
)
print(ruleset)
all_match_(egraph, ruleset)
egraph.to_mermaid().view_()
