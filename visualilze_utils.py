from typing import NamedTuple, List, Tuple, FrozenSet, Iterable


def rows(row: Iterable[str]) -> str:
    return '\n'.join(row)


class MermaidGraph(NamedTuple):
    sub_graphs: List[FrozenSet[str]]
    links: List[Tuple[str, str]]
    sub_graph_links: List[Tuple[int, int]]
    sub_graphs_prefix: str = 'sub_graph'
    title: str = "graph"

    def display(self) -> str:
        base = f"flowchart RL"
        subgraph_strs = [rows((f"subgraph {self.sub_graphs_prefix}{i}", rows(sub_g), "end"))
                         for i, sub_g in enumerate(self.sub_graphs)]
        subgraph_links = [f"{self.sub_graphs_prefix}{i} --> {self.sub_graphs_prefix}{j}"
                          for i, j in self.sub_graph_links]
        links = [f"{i} --> {j}" for i, j in self.links]

        return rows((base, rows(subgraph_strs), rows(subgraph_links), rows(links)))

    def html(self) -> str:
        return f"""
        <html lang="en">
        <head>
            <meta charset="utf-8" />
        </head>
        <body>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{ startOnLoad: true }});
            </script>

            <div class="mermaid">
            {self.display()}
            </div>
        </body>
        """
