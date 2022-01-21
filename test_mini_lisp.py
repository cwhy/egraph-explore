from __future__ import annotations

from mini_lisp.core import tokenize, parse_tokens, parse
from mini_lisp.core_types import Symbol
from mini_lisp.program import FreeAst, Program

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2)"
example_tokens = tokenize(example)
result = parse_tokens(example_tokens)
parsed = parse(example)
symbols = {Symbol(0): '/', Symbol(1): '^', Symbol(2): '*', Symbol(3): '+', Symbol(4): 'x', Symbol(5): '-'}
all_symbols = parsed.get_symbols()
freed = parsed.unfill(all_symbols, FreeAst)
assert all_symbols.from_symbol == symbols
print(all_symbols)
print(Program.parse(example).display)
