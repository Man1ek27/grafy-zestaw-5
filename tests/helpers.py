"""Wspólne funkcje testów: wczytywanie przykładów i wzorcowy maksymalny przepływ."""

from pathlib import Path

import networkx as nx

from graph_cli.network import parse_flow_network

EXAMPLES = Path(__file__).parents[1] / "examples"

# rys. 2 z input_5.pdf: przepływ f(u, v) na łukach sieci z rys. 1
# (s = 1, a..i = 2..10, t = 11)
FIGURE_2_FLOW = {
    (1, 2): 10,
    (1, 3): 3,
    (1, 4): 6,
    (2, 3): 5,
    (2, 5): 0,
    (2, 6): 5,
    (3, 6): 2,
    (3, 7): 6,
    (4, 5): 5,
    (4, 7): 1,
    (5, 9): 5,
    (6, 5): 0,
    (6, 10): 7,
    (7, 8): 7,
    (8, 11): 7,
    (9, 7): 0,
    (9, 8): 0,
    (9, 11): 5,
    (10, 11): 7,
}


def load(name):
    return parse_flow_network((EXAMPLES / name).read_text(encoding="utf-8"))


def reference_max_flow(network):
    """Wzorzec do porównań: maximum_flow_value z NetworkX (algorytm push-relabel)."""
    graph = nx.DiGraph()
    graph.add_nodes_from(network.graph.nodes())
    for (u, v), c in network.capacity.items():
        graph.add_edge(u, v, capacity=c)
    return nx.maximum_flow_value(graph, network.source, network.sink)
