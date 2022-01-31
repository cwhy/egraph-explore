from __future__ import annotations

from typing import Union, TypeVar, Type, List, Protocol, ItemsView, Iterator, Tuple, Mapping, Generator

from mini_lisp.core_types import AstLeaf, AstNode, AstParent, Number, AstLeafType, Symbol

MyMapping = Mapping

J = TypeVar("J", bound=AstLeaf)
V = TypeVar("V", bound=AstLeaf)
E = TypeVar("E", bound=Union[Number, AstLeaf])
D = TypeVar("D", bound=AstParent)

Out = Union[V, E]


def tree_replace(ast: AstNode[E],
                 table: MyMapping[Out, Out],
                 key_type: Type[E],
                 dest_type: Type[AstParent[Out]]) -> AstNode[Out]:
    if isinstance(ast, AstParent):
        args: List[AstNode[Out]] = []
        for arg in ast.args:
            args.append(tree_replace(arg, table, key_type, dest_type))
        return dest_type(tuple(args))
    elif isinstance(ast, key_type):
        # if arg is not in table, just return it
        return table.get(ast, ast)
    else:
        assert isinstance(ast, Number)
        return ast


graph_space = '   '
graph_branch = '║  '
graph_tee = '╟─ '
graph_last = '╙─ '


def tree_display(tree: AstNode) -> str:
    # if isinstance(tree, AstParent):
    # recursive type.. sigh
    if isinstance(tree, AstParent):
        return tree_parent_display(tree)
    else:
        return tree.display


def tree_parent_display(tree: AstParent[AstLeaf]) -> str:
    return tree.args[0].display + "\n" + "\n".join(tree_display_helper(tree, ""))


def tree_display_helper(tree: AstParent, prefix: str) -> Generator[str, str, None]:
    pointers = [graph_tee] * (len(tree.args) - 2) + [graph_last]
    for pointer, arg in zip(pointers, tree.args[1:]):
        if isinstance(arg, AstParent):
            yield prefix + pointer + arg.args[0].display
            extension = graph_branch if pointer == graph_tee else graph_space
            # yield prefix + extension + "╽"
            yield from tree_display_helper(arg, prefix + extension)
        else:
            yield prefix + pointer + arg.display


def tree_display_short(tree: AstNode) -> str:
    if isinstance(tree, AstParent):
        args = " ".join(tree_display_short(arg) for arg in tree.args)
        return f"({args})"
    else:
        assert isinstance(tree, AstLeaf)
        if isinstance(tree, Symbol):
            return tree.letter
        elif isinstance(tree, Number):
            return str(tree.value)
        else:
            return tree.display
