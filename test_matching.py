from __future__ import annotations

from mini_lisp.core import parse
from mini_lisp.patterns import PartialProgram, match
from mini_lisp.rules import Rule

example_partial = "(/ (^ (* (+ 1 ?y 3) ?x 4) (- 2)) 2)"
print(PartialProgram.parse(example_partial).display)


source_str = "(/ (^ (* (+ 1 2 3) x 4) (* 0 (- 2))) (* 1 2))"
source = parse(source_str)
print(source.display)
print(source_str)

example1 = "(* 1 ?x)"
print(f"Trying to match {example1}.....")
pattern = PartialProgram.parse(example1)
print(pattern.display)
match_result = match(source, pattern.partial_ast)
print(match_result[0])

example1 = "?x"
print(f"Trying to match {example1}.....")
pattern = PartialProgram.parse(example1).partial_ast
print(pattern.display)
match_results = match(source, pattern)
print(match_results)

#%%
rule = Rule.parse('(* 0 a)', '0')
print(match(source, rule.lhs))
k = rule.match_ast(source)
print(k)
print(next(iter(k)).display())
