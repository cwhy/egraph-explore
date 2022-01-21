from typing import NamedTuple, Literal

from mini_lisp.core import Symbols, parse
from mini_lisp.core_types import Symbol
from mini_lisp.patterns import PartialAst

RuleType = Literal['Rewrite', 'Equality']
ops = frozenset({'+', '-', '*', '/', '^'})


class Rule(NamedTuple):
    l: PartialAst
    r: PartialAst
    symbols: Symbols
    type: RuleType

    @property
    def display(self):
        return f"LHS: \n{self.l.display}\nRHS: \n{self.r.display}\n , where {self.symbols}"

    def __repr__(self):
        return self.display

    @classmethod
    def parse(cls, l: str, r: str,
              rule_type: RuleType = 'Rewrite') -> 'Rule':
        ast_l = parse(l)
        ast_r = parse(r)
        common_vars = ast_l.get_symbols().to_symbol.keys() & ast_r.get_symbols().to_symbol.keys()
        common_vars -= ops
        to_symbol = {v: Symbol(i) for i, v in enumerate(common_vars)}
        symbols = Symbols.from_to_symbol(to_symbol)
        return Rule(
            l=ast_l.unfill(symbols, PartialAst),
            r=ast_r.unfill(symbols, PartialAst),
            symbols=symbols,
            type=rule_type
        )


rule = Rule.parse('(* a b)', '(* b a)')
print(rule)
rule = Rule.parse('(* 1 a)', '(* a)')
print(rule)
rule = Rule.parse('(* a a)', '(^ a 2)')
print(rule)
rule = Rule.parse('(+ (* a c) (* a d))', '(* a (+ c d))')
print(rule)
