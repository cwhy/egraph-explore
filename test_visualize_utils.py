from visualilze_utils import MermaidGraph

g = MermaidGraph(sub_graphs=
             [frozenset(["a", "b"]), frozenset(["c"])],
             sub_graph_links=[(0, 1)],
             links=[("a", "b"), ("b", "c")],
             sub_graphs_prefix="S")
k = g.html()
print(k)
