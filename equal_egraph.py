from __future__ import annotations

from egraph import EGraph, AstP
from mini_lisp.core_types import AstParent


def print_result(fn):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        print(f"result: {result}")
        return result

    return wrapper


@print_result
def euqal_ast_class_node(graph: EGraph, class_node: AstP, to_test: AstP) -> bool:
    print(f"checking \n {class_node.display}\n == \n {to_test.display}")
    if isinstance(to_test, AstParent):
        if not isinstance(class_node, AstParent):
            return False
        else:
            for arg1, arg2 in zip(class_node.args[1:], to_test.args[1:]):
                assert arg1 in graph.registry
                if not equal_ast_node(graph, arg1, arg2):
                    return False
            else:
                return True
    else:
        if isinstance(class_node, AstParent):
            return False
        elif to_test == class_node:
            return True
        else:
            if to_test in graph.registry:
                assert class_node in graph.registry
                return graph.registry[to_test] == graph.registry[class_node]
            else:
                return False


def equal_ast_node(graph: EGraph, node: AstP, to_test: AstP) -> bool:
    class_id = graph.registry[node]
    for class_node in graph.classes[class_id]:
        if euqal_ast_class_node(graph, class_node, to_test):
            return True
    else:
        return False


def equal_ast(graph: EGraph, to_test: AstP) -> bool:
    return equal_ast_node(graph, next(iter(graph.classes[graph.root_class])), to_test)
