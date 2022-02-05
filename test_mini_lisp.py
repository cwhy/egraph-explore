from __future__ import annotations


from mini_lisp.core import tokenize, parse_tokens, parse, Symbols, get_symbols
from mini_lisp.core_types import Symbol, Variable
from mini_lisp.patterns import PartialProgram, match
from mini_lisp.program import FreeAst, Program
from mini_lisp.rules import Rule
from mini_lisp.tree_utils import tree_replace

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2)"
example_tokens = tokenize(example)
result = parse_tokens(example_tokens)
print(result)
parsed = parse(example)

#%%
symbols = {Symbol(0): Variable('/'),
           Symbol(1): Variable('^'),
           Symbol(2): Variable('*'),
           Symbol(3): Variable('+'),
           Symbol(4): Variable('x'),
           Symbol(5): Variable('-')}

print(parsed.display)
all_symbols = get_symbols(parsed)
print(all_symbols)
print(Symbols.from_from_symbol(symbols))
assert all_symbols.from_symbol == symbols
print(Program.parse(example).display)

freed = tree_replace(parsed, all_symbols.to_symbol, Variable, FreeAst)
#%%

example_partial = "(/ (^ (* (+ 1 ?y 3) ?x 4) (- 2)) 2)"
print(PartialProgram.parse(example_partial).display)

pattern = PartialProgram.parse("(* 1 ?x)")
print(pattern.display)
source = parse("(/ (^ (* (+ 1 2 3) x 4) (* 1 (- 2))) (* 1 2))")
print(source.display)
print("Trying to match.....")
result = match(source, pattern.partial_ast)
print(result)

rule = Rule.parse('(* a b)', '(* b a)')
print(rule)
rule = Rule.parse('(* 1 a)', 'a')
print(rule)
rule = Rule.parse('(* a a)', '(^ a 2)')
print(rule)
rule = Rule.parse('(+ (* a c) (* a d))', '(* a (+ c d))')
print(rule)
