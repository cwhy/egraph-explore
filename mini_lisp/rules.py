from typing import NamedTuple, Literal, List, FrozenSet

from mini_lisp.core import Symbols, parse, get_symbols
from mini_lisp.core_types import Symbol, AstNode, AstLeaf, Variable
from mini_lisp.patterns import PartialAst
from mini_lisp.tree_utils import tree_replace, tree_display_short

ops = frozenset(Variable(x) for x in {'+', '-', '*', '/', '^', '<<'})


class Rule(NamedTuple):
    l: AstNode[AstLeaf]
    r: AstNode[AstLeaf]
    symbols: Symbols

    @property
    def display(self):
        symbol_str = f", where {self.symbols}\n" if len(self.symbols.to_symbol) != 0 else ""
        return f"LHS: \n{self.l.display}\nRHS: \n{self.r.display}\n " + symbol_str

    @property
    def short_display(self) -> str:
        return f"{tree_display_short(self.l)} -> {tree_display_short(self.r)}"

    def __repr__(self):
        return self.short_display

    @classmethod
    def parse(cls, l: str, r: str) -> 'Rule':
        ast_l = parse(l)
        ast_r = parse(r)
        common_vars = get_symbols(ast_l).to_symbol.keys() & get_symbols(ast_r).to_symbol.keys()
        common_vars -= ops
        to_symbol = {v: Symbol(i) for i, v in enumerate(common_vars)}
        symbols = Symbols.from_to_symbol(to_symbol)
        return Rule(
            l=tree_replace(ast_l, symbols.to_symbol, Variable, PartialAst),
            r=tree_replace(ast_r, symbols.to_symbol, Variable, PartialAst),
            symbols=symbols
        )


# Examples:
# """
# (+ x 0) -> x
# (+ x y z) == (+ y z x)
# """
RuleSet = FrozenSet[Rule]


def parse_ruleset(rules_str: str) -> RuleSet:
    rules = set()
    for row in rules_str.split('\n'):
        if "->" in row:
            rules.add(Rule.parse(*row.split('->')))
        elif "==" in row:
            eq_rules = row.split('==')
            rules.add(Rule.parse(*eq_rules))
            rules.add(Rule.parse(*reversed(row.split('=='))))
    return frozenset(rules)
