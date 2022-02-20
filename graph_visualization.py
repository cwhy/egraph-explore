from __future__ import annotations

import math
import tempfile
import webbrowser
from functools import cached_property, lru_cache
import random
from typing import NamedTuple, List, Tuple, FrozenSet, Iterable, Optional, Dict, Iterator, Generator, TypeVar, Callable


# from http://alienryderflex.com/hsp.html
def is_dark_hsp(r: int, g: int, b: int) -> bool:
    hsp = 0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b)
    if hsp > 127.5 ** 2:
        return False
    else:
        return True


# from https://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
kelly_colors_hex = [
    0xFFB300,  # Vivid Yellow
    0x803E75,  # Strong Purple
    0xFF6800,  # Vivid Orange
    0xA6BDD7,  # Very Light Blue
    0xC10020,  # Vivid Red
    0xCEA262,  # Grayish Yellow
    0x817066,  # Medium Gray

    # The following don't work well for people with defective color vision
    0x007D34,  # Vivid Green
    0xF6768E,  # Strong Purplish Pink
    0x00538A,  # Strong Blue
    0xFF7A5C,  # Strong Yellowish Pink
    0x53377A,  # Strong Violet
    0xFF8E00,  # Vivid Orange Yellow
    0xB32851,  # Strong Purplish Red
    0xF4C800,  # Vivid Greenish Yellow
    0x7F180D,  # Strong Reddish Brown
    0x93AA00,  # Vivid Yellowish Green
    0x593315,  # Deep Yellowish Brown
    0xF13A13,  # Vivid Reddish Orange
    0x232C16,  # Dark Olive Green
]


def hex2str(hex_color: int) -> str:
    return f"#{hex_color:06x}"


def hex2rgb(hex_color: int) -> Tuple[int, int, int]:
    return hex_color >> 16, hex_color >> 8 & 0xFF, hex_color & 0xFF


def shuffler_style_gen(n: int, styles: Tuple[int, ...]) -> Callable[[int], Tuple[int, ...]]:
    all_styles = list(range(math.prod(styles)))
    random.shuffle(all_styles)

    def decode(i: int) -> Tuple[int, ...]:
        return tuple(all_styles[i] % s for s in styles)

    return lambda i: decode(all_styles[i % len(all_styles)])


def rows(row: Iterable[str]) -> str:
    return '\n'.join(row)


class NodeStyle(NamedTuple):
    fill: int = 3
    stroke: int = 5
    stroke_dasharray: int = 0
    shape: int = 0

    color_map: List[int] = kelly_colors_hex
    dasharray_opts: List[Optional[Tuple[int, int]]] = frozenset({None, (5, 5)})
    shape_opts: List[str] = [{'()', '[]', '(())', '[[]]', '>]',
                              '{}', '{{}}', '//', '\\\\', '/\\', '\\/'}]

    def render_dasharray(self) -> str:
        dash_array_type = self.dasharray_opts[self.stroke_dasharray]
        if dash_array_type is not None:
            return f"stroke-dasharray: {dash_array_type[0]} {dash_array_type[1]}"
        else:
            return ""

    def render_shape(self, label: str) -> str:
        assert self.shape < len(self.shape_opts)
        s = self.shape_opts[self.shape]
        begin = s[:len(s)//2]
        ends = s[len(s)//2:]

    def render_color(self) -> str:
        if is_dark_hsp(*hex2rgb(self.color_map[self.fill])):
            return "color: white"
        else:
            return "color: black"

    def render_style(self) -> str:
        return ",".join([
            f"fill: {hex2str(self.color_map[self.fill])}",
            f"stroke: {hex2str(self.color_map[self.stroke])}",
            self.render_dasharray(),
            f"color: {hex2str(self.color_map[self.stroke])}",
            "stroke-width:4px"
        ])

    @classmethod
    def get_style_gen(cls, n: int) -> Callable[[int], NodeStyle]:
        new = cls()
        styles_n = (len(new.color_map), len(new.color_map),
                    len(new.dasharray_opts), len(new.shape_opts))
        int_style_gen = shuffler_style_gen(n, styles_n)

        def style_gen(i: int) -> NodeStyle:
            return NodeStyle(*int_style_gen(i))

        return style_gen


class MermaidGraph(NamedTuple):
    sub_graphs: List[FrozenSet[str]]
    links: List[Tuple[str, str]]
    sub_graph_links: List[Tuple[int, int]]
    node_names: Optional[List[str]] = None
    node_styles: Optional[Dict[int, NodeStyle]] = None

    @classmethod
    def init_all_subgraph(cls,
                          sub_graphs: List[FrozenSet[str]],
                          links: List[Tuple[str, str]],
                          sub_graph_links: List[Tuple[int, int]],
                          node_names: Optional[List[str]] = None,
                          node_styles: Optional[Dict[int, str]] = None) -> MermaidGraph:
        nodes = set().union(*sub_graphs)
        for i_node, j_node in links:
            assert i_node in nodes
            assert j_node in nodes
        for i, j in sub_graph_links:
            assert i < len(sub_graphs)
            assert j < len(sub_graphs)
        assert len(sub_graphs) == len(node_names)
        assert len(nodes) == len(node_styles)
        return MermaidGraph(sub_graphs, links, sub_graph_links, node_names, node_styles)

    def subgraph_name(self, i: int) -> str:
        if self.node_names is None:
            return f"subgraph"
        else:
            assert len(self.node_names) == len(self.sub_graphs)
            return self.node_names[i]

    def subgraph_id(self, i: int) -> str:
        return f"{i}[{self.subgraph_name(i)}]"

    @property
    def node_ids(self) -> Dict[str, int]:
        # need to do this because mermaid doesn't like special characters
        # give up on lru_cache here, the performance really doesn't matter
        return {v: i for i, v in enumerate(set().union(*self.sub_graphs).union(*sum(self.links, ())))}

    def node_tag(self, node: str) -> str:
        return f'N{self.node_ids[node]}["{node}"]'

    def display(self) -> str:
        base = f"flowchart LR"
        subgraph_strs = [rows((f"subgraph {self.subgraph_id(i)}",
                               rows(self.node_tag(s) for s in sub_g),
                               "end"))
                         for i, sub_g in enumerate(self.sub_graphs)]
        subgraph_links = [f"{self.subgraph_id(i)} --> {self.subgraph_id(j)}"
                          for i, j in self.sub_graph_links]
        links = [f"{self.node_tag(i)} --> {self.node_tag(j)}" for i, j in self.links]
        node_styles = [f"style {i} {v.render_style()}"
                       for i, v in self.node_styles.items()
                       ] if self.node_styles is not None else []

        return rows((base, rows(subgraph_strs), rows(subgraph_links), rows(links), rows(node_styles)))

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

    def view_(self) -> None:
        open_in_browser_(self.html())


def open_in_browser_(html_content: str):
    path = tempfile.NamedTemporaryFile(suffix=".html", delete=False).name
    with open(path, 'w') as f:
        f.write(html_content)
    webbrowser.open('file://' + path)
