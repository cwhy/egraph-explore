from __future__ import annotations

from mini_lisp.core import parse
from mini_lisp.patterns import PartialProgram, match

example_partial = "(/ (^ (* (+ 1 ?y 3) ?x 4) (- 2)) 2)"
print(PartialProgram.parse(example_partial).display)

pattern = PartialProgram.parse("(* 1 ?x)")
print(pattern.display)
source = parse("(/ (^ (* (+ 1 2 3) x 4) (* 1 (- 2))) (* 1 2))")
print(source.display)

print("Trying to match.....")
match_result = match(source, pattern.partial_ast)
print(match_result[0])
print(match_result[1])
