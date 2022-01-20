from __future__ import annotations

from typing import TypeVar, Type, Protocol, Any, List, runtime_checkable

graph_space = '   '
graph_branch = '║  '
graph_tee = '╟─ '
graph_last = '╙─ '


@runtime_checkable
class AstType(Protocol):
    op: Any
    args: List[Any, AstType]


def display_ast_helper(ast: AstType, prefix: str) -> str:
    pointers = [graph_tee] * (len(ast.args) - 1) + [graph_last]
    for pointer, arg in zip(pointers, ast.args):
        if isinstance(arg, AstType):
            yield prefix + pointer + str(arg.op)
            extension = graph_branch if pointer == graph_tee else graph_space
            yield prefix + extension + "╽"
            yield from display_ast_helper(arg, prefix + extension)
        else:
            yield prefix + pointer + str(arg)
