## Generic good resources:
- Paper for EGG https://arxiv.org/pdf/2004.03082.pdf
- Talk for EGG: https://www.youtube.com/watch?v=LKELTEOFY-s&t=541s
- Code for EGG(Rust): https://github.com/mwillsey/egg/blob/main/src/egraph.rs

- Thesis about Egraph in Julia: https://arxiv.org/pdf/2112.14714.pdf
- Max Willsey's Thesis: https://www.mwillsey.com/thesis/thesis.pdf


## EGraph Essential Compoments:
### Input and parsing:
- A mini lisp-like compute graph
- Partial parsing for rule(sets)

### EGraph maintanence:
- add Enodes and remove Enodes
- Current implementation:
    - Python Set merge
    - not very efficient
        - alternative: union find

### EMatch
- Pattern matching: given a partial ast with queries, find matching parts in the graph
- Current implementation: 
    - Inefficent graph traversal
    - Other implementations:
        - Simplify:
            - https://www.philipzucker.com/egraph-2/
            - https://www.hpl.hp.com/techreports/2003/HPL-2003-148.pdf 
        - Z3(too complex):
            - https://leodemoura.github.io/files/ematching.pdf
        - Relational EMatching:
            - talk:
                - https://www.youtube.com/watch?v=e2EtwjgZMnY
            - paper:
                - https://ztatlock.net/pubs/2022-popl-rematch/2022-popl-rematch.pdf
            - other slides:
                - https://effect.systems/doc/pldi-2021-src/slides.pdf
                - https://effect.systems/doc/ug-thesis/talk.pdf
            - thesis:
                - https://effect.systems/doc/ug-thesis/thesis.pdf
            - code:
                - https://github.com/yihozhang/relational-ematching-benchmark
            - Generic Join code
                - https://github.com/mwillsey/qry/blob/main/src/lib.rs


### EGraph saturation (matching order):
- Using RL(tbd later)
