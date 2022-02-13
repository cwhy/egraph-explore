from __future__ import annotations

from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.program import Program

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2)"
# z = Program.parse(example).free_ast
g = EGraph.from_ast(parse(example))
print(g.root_node.display)


