from __future__ import annotations

from typing import Union, Dict, TypeVar, Type, List, Callable, Tuple

from mini_lisp.core_types import Symbol, AstLeaf, AstNode, AstParent, Variable, Float

J = TypeVar("J", bound=AstLeaf)
K = TypeVar("K", bound=AstLeaf)
V = TypeVar("V", bound=AstLeaf)
D = TypeVar("D", bound=AstParent)


def tree_replace(ast: AstNode[J],
                 table: Dict[K, V],
                 key_type: Type[K],
                 dest_type: Type[D]) -> Union[D, J, V]:
    if isinstance(ast, AstParent):
        args: List[Union[J, V]] = []
        for arg in ast.args:
            args.append(tree_replace(arg, table, key_type, dest_type))
        return dest_type(tuple(args))
    elif isinstance(ast, key_type):
        # if arg is not in table, just return it
        return table.get(ast, ast)
    else:
        assert isinstance(ast, Float)
        return ast


graph_space = '   '
graph_branch = '║  '
graph_tee = '╟─ '
graph_last = '╙─ '
TF = TypeVar("TF", bound=AstLeaf)


def tree_display(tree: AstNode[TF], tree_type: Type[AstNode[TF]]) -> str:
    return str(tree.args[0]) + "\n" + "\n".join(tree_display_helper(tree, "", tree_type))


def tree_display_helper(tree: TF, prefix: str, tree_type: Type[TF]) -> str:
    pointers = [graph_tee] * (len(tree.args) - 2) + [graph_last]
    for pointer, arg in zip(pointers, tree.args[1:]):
        if isinstance(arg, tree_type):
            yield prefix + pointer + str(arg.args[0])
            extension = graph_branch if pointer == graph_tee else graph_space
            # yield prefix + extension + "╽"
            yield from tree_display_helper(arg, prefix + extension, tree_type)
        else:
            yield prefix + pointer + str(arg)
