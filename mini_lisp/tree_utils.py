from __future__ import annotations

from typing import TypeVar, Mapping, Generator

from mini_lisp.core_types import AstLeaf, AstNode, AstParent, Number, Symbol

MyMapping = Mapping

T = TypeVar("T")


# No types for you until mypy or pycharm gets better
# I am too tired.
def tree_replace(ast,
                 table,
                 key_type,
                 dest_type):
    if isinstance(ast, AstParent):
        args = []
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
