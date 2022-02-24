from __future__ import annotations

from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.program import Program
from mini_lisp.rules import Rule

# example = "(/ (^ (* (+ (* 0 3) 2 3) x 4) (- 2)) (- 2))"
example2 = "(/ (* a 2) 2)"
# z = Program.parse(example).free_ast
g = EGraph.from_ast(parse(example2))
print(next(iter(g.root_nodes)).display)
g.to_mermaid().view_()

# rule = Rule.parse('(* 0 a)', '0')
rule2 = Rule.parse('(* x 2)', '(<< x 1)')
res = g.match_rule(rule2)
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
print(g)
# print(g.to_mermaid().display())
g.to_mermaid().view_()

rule2 = Rule.parse('(/ (* x y) z)', '(* x (/ y z))')
res = g.match_rule(rule2)
print(res)
assert len(res) >= 1
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
g.to_mermaid().view_()

rule2 = Rule.parse('(/ x x)', '1')
res = g.match_rule(rule2)
next_res = next(iter(res))
print(next_res.display())
g.apply_(next_res)
g.to_mermaid().view_()

rule2 = Rule.parse('(* x 1)', 'x')
res = g.match_rule(rule2)
g.apply_(next(iter(res)))
g.to_mermaid().view_()
