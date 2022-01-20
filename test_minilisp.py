#%%
from minilisp import tokenize, parse_tokens, parse, Ast
from pattern import parse2partial, parse_partial, match

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2)"
example_tokens = tokenize(example)
result = parse_tokens(example_tokens)
result2 = parse(example)

actual = Ast(op='/', args=[
    Ast(op='^', args=[
        Ast(op='*', args=[
            Ast(op='+', args=[1.0, 2.0, 3.0]), 'x', 4.0]),
        Ast(op='-', args=[2.0])]),
    2.0])

assert result == actual
assert result2 == actual
program = actual.decoupled
print(program)


print(program.ast)
print(parse2partial(example, ("/", "^", "*", "+", "-")))

example_partial = "(/ (^ (* (+ 1 ?y 3) ?x 4) (- 2)) 2)"
print(parse_partial(example_partial))

pattern = parse_partial("(* 1 ?x)")
source = parse("(/ (^ (* (+ 1 2 3) x 4) (* 1 (- 2))) (* 1 2))")

result = match(source, pattern.partial_ast)
print(result)