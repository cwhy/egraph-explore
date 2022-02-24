from graph_visualization import MermaidGraph, open_in_browser_, shuffler_style_gen

g = MermaidGraph(sub_graphs=
                 [frozenset([0, 1]), frozenset([2, 3])],
                 sub_graph_links=[(1, 0)],
                 links=[(0, 1), (1, 2)])
k = g.html()
print(k)

open_in_browser_(k)

style_gen = shuffler_style_gen((3, 4, 5))
print(list(style_gen(i) for i in range(20)))

g = MermaidGraph(sub_graphs=
                 [frozenset([0, 1]), frozenset([2]), frozenset([3])],
                 sub_graph_links=[(1, 0)],
                 links=[(0, 1), (2, 3)],
                 node_names={0: "node A", 1: "node B", 2: "node A"})

g.view_()
