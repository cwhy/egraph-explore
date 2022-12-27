from typing import NamedTuple, Literal, List, FrozenSet, Iterable

from mini_lisp.core import Symbols, parse, get_symbols, RawLeaves, Ast
from mini_lisp.core_types import Symbol, AstNode, AstLeaf, Variable, AstParent
from mini_lisp.patterns import PartialAst, match, MatchResult
from mini_lisp.tree_utils import tree_replace, tree_display_short

OPs = frozenset(Variable(x) for x in {'+', '-', '*', '/', '^', '<<'})

AstP = AstNode[RawLeaves]


class RuleMatchResult(NamedTuple):
    index: AstP
    to: AstP

    def display(self):
        return f"index: \n {self.index.display}\n to: \n {self.to.display}"


class Rule(NamedTuple):
    lhs: AstNode[AstLeaf]
    rhs: AstNode[AstLeaf]
    symbols: Symbols

    @property
    def display(self):
        symbol_str = f", where {self.symbols}\n" if len(self.symbols.to_symbol) != 0 else ""
        return f"LHS: \n{self.lhs.display}\nRHS: \n{self.rhs.display}\n " + symbol_str

    @property
    def short_display(self) -> str:
        return f"{tree_display_short(self.lhs)} -> {tree_display_short(self.rhs)}"

    def __repr__(self):
        return self.short_display

    @classmethod
    def parse(cls, l: str, r: str, custom_ops: Iterable[str] = tuple()) -> 'Rule':
        ast_l = parse(l)
        ast_r = parse(r)
        symbol_keys = get_symbols(ast_l).to_symbol.keys() | get_symbols(ast_r).to_symbol.keys()
        symbol_keys -= OPs
        symbol_keys -= set(custom_ops)
        to_symbol = {v: Symbol(i) for i, v in enumerate(symbol_keys)}
        symbols = Symbols.from_to_symbol(to_symbol)
        return Rule(
            lhs=tree_replace(ast_l, symbols.to_symbol, Variable, PartialAst),
            rhs=tree_replace(ast_r, symbols.to_symbol, Variable, PartialAst),
            symbols=symbols
        )

    def apply(self, match_result: MatchResult) -> RuleMatchResult:
        return RuleMatchResult(
            index=match_result.node,
            to=tree_replace(self.rhs, match_result.symbols.from_symbol, Symbol, Ast)
        )

    def apply_all(self, match_results: Iterable[MatchResult]) -> AstP:
        return frozenset(self.apply(x) for x in match_results)

    def match_ast(self, ast: AstP) -> FrozenSet[RuleMatchResult]:
        return self.apply_all(match(self.lhs, ast))


# Examples:
# """
# (+ x 0) -> x
# (+ x y z) == (+ y z x)
# """
RuleSet = FrozenSet[Rule]


def parse_ruleset(rules_str: str, trim: bool = False, custom_ops: Iterable[str] = tuple()) -> RuleSet:
    rules = set()
    for row in rules_str.split('\n'):
        if "->" in row:
            rules.add(Rule.parse(*row.split('->')), custom_ops)
        elif "==" in row:
            eq_rules = row.split('==')
            rules.add(Rule.parse(*eq_rules, custom_ops))
            rules.add(Rule.parse(*reversed(row.split('=='))), custom_ops)
    if trim:
        return trim_ruleset(rules)
    else:
        return frozenset(rules)


def trim_ruleset(rules: Iterable[Rule]) -> RuleSet:
    new_rules = frozenset(
        filter(lambda rule:
               not (isinstance(rule.rhs, AstParent) and not isinstance(rule.lhs, AstParent)),
               rules))
    return new_rules
