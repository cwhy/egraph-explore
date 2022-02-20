from graph_visualization import MermaidGraph, open_in_browser_, shuffler_style_gen

g = MermaidGraph(sub_graphs=
                 [frozenset(["a", "b"]), frozenset(["a", "c"])],
                 sub_graph_links=[(1, 0)],
                 links=[("a", "b"), ("b", "c")])
k = g.html()
print(k)

open_in_browser_(k)

style_gen = shuffler_style_gen(20, (3, 4, 5))
print(list(style_gen(i) for i in range(20)))

g = MermaidGraph(sub_graphs=
                 [frozenset(["a", "b"]), frozenset(["c"]), frozenset(["d"])],
                 sub_graph_links=[(1, 0)],
                 links=[("a", "b"), ("b", "c")],
                 sub_graph_names=["A", "B", "A"])

g.view_()
