from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.rules import parse_ruleset
from test_equality import saturate

example = "(w3j l1 l2 l3 s1 s2 s3)"
g = EGraph.from_ast(parse(example))

# rule1: cyclic permutation
# rule2: swap permutation, introduce parity operator: P(l1, l2, l3) = (-1)^(l1 + l2 + l3)
rset = parse_ruleset(
    """
    (w3j l1 l2 l3 s1 s2 s3) == (w3j l2 l3 l1 s2 s3 s1)
    (w3j l1 l2 l3 s1 s2 s3) == (* (P l2 l1 l3) (w3j l2 l1 l3 s2 s1 s3))
    """, 
    custom_ops=['w3j', 'P'], trim=True
)
[print(r.display) for r in rset]
saturate(g, rset)
g.to_mermaid().view_()
