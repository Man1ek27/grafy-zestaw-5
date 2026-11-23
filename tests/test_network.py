import pytest

from graph_cli.network import layers_from_bfs, parse_flow_network, vertex_names
from helpers import load


def test_layers_of_figure_1():
    network = load("input-5.txt")
    assert network.source == 1 and network.sink == 11
    assert network.layers == [[1], [2, 3, 4], [5, 6, 7], [8, 9, 10], [11]]


def test_unreachable_vertex_gets_own_layer_before_sink():
    network = parse_flow_network("4\n1 2 3\n2 4 3\n3 2 1\n")
    assert network.layers == [[1], [2], [3], [4]]
    graph = network.graph
    graph.remove_edge(2, 4)
    assert layers_from_bfs(graph, 1, 4) == [[1], [2], [3], [4]]


def test_vertex_names():
    names = vertex_names(load("cormen-6.txt"))
    assert names == {1: "s", 2: "2", 3: "3", 4: "4", 5: "5", 6: "t"}


@pytest.mark.parametrize(
    "text",
    [
        "1\n",
        "3\n1 2 0\n2 3 4\n",
        "3\n1 2 -1\n2 3 4\n",
        "3\n1 2 5\n2 1 5\n2 3 5\n",
        "3\n1 2 5\n3 2 5\n",
        "3\n1 2 5\n2 3 4\n3 2 1\n",
        "3\n1 2 5\n2 3\n",
        "",
    ],
)
def test_invalid_networks(text):
    with pytest.raises(ValueError):
        parse_flow_network(text)
