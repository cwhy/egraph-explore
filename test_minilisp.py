from minilisp import tokenize, parse_tokens, parse, Ast, extract_var_helper

example = "(/ (^ (* (+ 1 2 3) x 4) (- 2)) 2 a)"
example_tokens = tokenize(example)
result = parse_tokens(example_tokens)
result2 = parse(example)

actual = Ast(op='/', args=[
    Ast(op='^', args=[
        Ast(op='*', args=[
            Ast(op='+', args=[1.0, 2.0, 3.0]), 'x', 4.0]),
        Ast(op='-', args=[2.0])]),
    2.0, 'a'])

assert result == actual
assert result2 == actual
k = extract_var_helper(actual, {})
print(k)
