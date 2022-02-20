from __future__ import annotations

from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.program import Program
from mini_lisp.rules import Rule

example = "(/ (^ (* (+ (* 0 3) 2 3) x 4) (- 2)) (- 2))"
# z = Program.parse(example).free_ast
g = EGraph.from_ast(parse(example))
print(g.root_node.display)
g.to_mermaid().view_()

rule = Rule.parse('(* 0 a)', '0')
res = g.match_rule(rule)
print(res)
g.apply_(next(iter(res)))
print(g)
print(g.to_mermaid().display())
g.to_mermaid().view_()

