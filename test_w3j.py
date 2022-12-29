from egraph import EGraph
from mini_lisp.core import parse
from mini_lisp.rules import parse_ruleset
from test_equality import saturate

example = "(* (w3j l1 l2 l3 s1 s2 s3) (w3j l2 l1 l3 s2p s1p s3p))"
g = EGraph.from_ast(parse(example))

# rule1: cyclic permutation
# rule2: swap permutation, introduce parity operator: P(l1, l2, l3) = (-1)^(l1 + l2 + l3)
# rule3: w3j to wigd
# rule4-5: * associativity and commutativity
rset = parse_ruleset(
    """
    (w3j l1 l2 l3 s1 s2 s3) == (w3j l2 l3 l1 s2 s3 s1)
    (w3j l1 l2 l3 s1 s2 s3) == (* P (w3j l2 l1 l3 s2 s1 s3))
    (* (w3j l1 l2 l3 s1 s2 s3) (w3j l1 l2 l3 s1p s2p s3p)) == (* (wigd l1 s1 s1p) (wigd l2 s2 s2p) (wigd l3 s3 s3p))
    (* (* a b) c) == (* a (* b c))
    (* a b) == (* b c)
    """, 
    custom_ops=['w3j', 'P', 'wigd'], trim=True
)
[print(r.display) for r in rset]
saturate(g, rset)
g.to_mermaid().view_()
