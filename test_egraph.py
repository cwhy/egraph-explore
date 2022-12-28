from __future__ import annotations

from pprint import pprint

from egraph import EGraph
from match_egraph import match_rule
from mini_lisp.core import parse
from mini_lisp.rules import Rule

example2 = "(/ (* a 2) 2)"
g = EGraph.from_ast(parse(example2))
print(next(iter(g.root_nodes)).display)
g.to_mermaid().view_()

rule2 = Rule.parse('(* x 2)', '(<< x 1)')
res = match_rule(g, rule2)
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
print(g)
g.to_mermaid().view_()

rule2 = Rule.parse('(/ (* x y) z)', '(* x (/ y z))')
res = match_rule(g, rule2)
print(res)
assert len(res) >= 1
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
g.to_mermaid().view_()

rule2 = Rule.parse('(/ x x)', '1')
res = match_rule(g, rule2)
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
pprint(g.classes)
pprint(g.registry)
g.to_mermaid().view_()

rule2 = Rule.parse('(* x 1)', 'x')
res = match_rule(g, rule2)
g.apply_(next(iter(res)))
g.to_mermaid().view_()


example = "(/ (^ (* (+ (* 0 3) 2 3) x 4) (- 2)) (- 2))"
# z = Program.parse(example).free_ast
g = EGraph.from_ast(parse(example))
print(next(iter(g.root_nodes)).display)
g.to_mermaid().view_()

rule = Rule.parse('(* 0 a)', '0')
res = match_rule(g, rule)
print(res)
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
print(g)
print(g.to_mermaid().display())
g.to_mermaid().view_()
