from __future__ import annotations

from typing import Union, Dict, TypeVar, Type

from mini_lisp.core_types import AstType, Symbol

TF = TypeVar("TF", bound=AstType)
TT = TypeVar("TT", bound=AstType)
K = TypeVar("K", bound=Union[Symbol, str])


def tree_replace(ast: TF,
                 table: Dict[K, Union[Symbol, str]],
                 key_type: Type[K],
                 from_type: Type[TF],
                 dest_type: Type[TT]) -> TT:
    args = []
    for arg in ast.args:
        if isinstance(arg, int) or isinstance(arg, float):
            args.append(arg)
        elif isinstance(arg, key_type):
            # if arg is not in free_table, just return it
            args.append(table.get(arg, arg))
        else:
            assert isinstance(arg, from_type)
            args.append(tree_replace(arg, table, key_type, from_type, dest_type))
    return dest_type(args)


graph_space = '   '
graph_branch = '║  '
graph_tee = '╟─ '
graph_last = '╙─ '


def tree_display(tree: TF, tree_type: Type[TF]) -> str:
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
