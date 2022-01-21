from __future__ import annotations

from mini_lisp.core import tokenize, parse_tokens, parse
from mini_lisp.core_types import Symbol
from mini_lisp.patterns import PartialProgram, match
from mini_lisp.program import FreeAst, Program

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2)"
example_tokens = tokenize(example)
result = parse_tokens(example_tokens)
print(result)
parsed = parse(example)
symbols = {Symbol(0): '/', Symbol(1): '^', Symbol(2): '*', Symbol(3): '+', Symbol(4): 'x', Symbol(5): '-'}
all_symbols = parsed.get_symbols()
freed = parsed.unfill(all_symbols, FreeAst)
assert all_symbols.from_symbol == symbols
print(all_symbols)
print(Program.parse(example).display)

example_partial = "(/ (^ (* (+ 1 ?y 3) ?x 4) (- 2)) 2)"
print(PartialProgram.parse(example_partial).display)

pattern = PartialProgram.parse("(* 1 ?x)")
source = parse("(/ (^ (* (+ 1 2 3) x 4) (* 1 (- 2))) (* 1 2))")
print(source.display)
result = match(source, pattern.partial_ast)
print(result)
