from __future__ import annotations

from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.rules import RuleSet, parse_ruleset, trim_ruleset


def all_match_(egraph: EGraph, rule_set: RuleSet, visualize_lvl: int =0, max_iter: int = 200) -> None:
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

all_match_(egraph, ruleset, visualize_lvl=2)
egraph.to_mermaid().view_()

example = "(^ (+ a 2) 2)"
g = EGraph.from_ast(parse(example))
g.to_mermaid().view_()
ruleset = parse_ruleset(
    """
    (* (+ x y) z) == (+ (* x z) (* y z))
    (* x y) == (* y x)
    (+ x y) == (+ y x)
    (* (* x y) z) == (* x (* y z))
    (+ (+ a b) c) == (+ a (+ b c))
    (/ x x) -> 1
    (* x 1) -> x
    (* x 2) == (<< x 1)
    (^ x 2) == (* x x)
    (^ x 1) -> x
    (^ x 0) -> 1
    """, trim=True
)
# (^ x n) == (* x (^ x (- n 1)))
all_match_(g, ruleset, visualize_lvl=1)