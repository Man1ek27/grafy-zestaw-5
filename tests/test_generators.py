import random

import pytest
from networkx import DiGraph

from graph_cli.generators import (
    add_random_arcs,
    connect_layers,
    random_flow_network,
    random_layers,
    random_weights,
)


def layer_arcs(network):
    """Łuki z warstwy i do i + 1 (zgodne z warstwami)."""
    layer_of = {v: i for i, layer in enumerate(network.layers) for v in layer}
    return {(u, v) for u, v in network.graph.edges() if layer_of[v] == layer_of[u] + 1}


@pytest.mark.parametrize("n_layers", [2, 3, 4])
def test_layers_have_two_to_n_vertices(n_layers):
    for seed in range(30):
        layers = random_layers(n_layers, random.Random(seed))
        assert len(layers) == n_layers + 2
        assert layers[0] == [1]
        assert all(2 <= len(layer) <= n_layers for layer in layers[1:-1])
        numbers = [v for layer in layers for v in layer]
        assert numbers == list(range(1, len(numbers) + 1))
        assert layers[-1] == [numbers[-1]]


@pytest.mark.parametrize("n_layers", [2, 3, 4, 6])
def test_network_satisfies_all_conditions(n_layers):
    for seed in range(50):
        network = random_flow_network(n_layers, random.Random(seed))
        graph, layers = network.graph, network.layers
        s, t = network.source, network.sink

        # z każdego wierzchołka warstwy i wychodzi łuk do warstwy i + 1
        # i do każdego wierzchołka warstwy i + 1 wchodzi łuk z warstwy i
        for i in range(len(layers) - 1):
            for u in layers[i]:
                assert any(graph.has_edge(u, v) for v in layers[i + 1])
            for v in layers[i + 1]:
                assert any(graph.has_edge(u, v) for u in layers[i])

        assert graph.in_degree(s) == 0
        assert graph.out_degree(t) == 0
        assert all(not graph.has_edge(v, u) for u, v in graph.edges())
        assert all(u != v for u, v in graph.edges())
        assert set(network.capacity) == set(graph.edges())
        assert all(1 <= c <= 10 for c in network.capacity.values())


def test_exactly_2n_random_arcs_are_added():
    rng = random.Random(5)
    layers = random_layers(3, rng)
    graph = DiGraph()
    for layer in layers:
        graph.add_nodes_from(layer)
    for i in range(len(layers) - 1):
        connect_layers(graph, layers[i], layers[i + 1], rng)
    before = graph.number_of_edges()
    add_random_arcs(graph, 6, layers[0][0], layers[-1][0], rng)
    assert graph.number_of_edges() == before + 6


def test_random_arcs_may_go_against_layers():
    backward = 0
    for seed in range(50):
        network = random_flow_network(3, random.Random(seed))
        layer_of = {v: i for i, layer in enumerate(network.layers) for v in layer}
        backward += sum(layer_of[v] <= layer_of[u] for u, v in network.graph.edges())
    assert backward > 0


def test_no_free_pair_for_random_arc():
    graph = DiGraph([(1, 2), (2, 3), (1, 3)])
    with pytest.raises(ValueError):
        add_random_arcs(graph, 1, 1, 3, random.Random(1))


def test_seed_gives_the_same_network():
    first = random_flow_network(4, random.Random(11))
    second = random_flow_network(4, random.Random(11))
    assert first.layers == second.layers
    assert first.capacity == second.capacity


@pytest.mark.parametrize("n_layers", [-1, 0, 1])
def test_too_few_layers(n_layers):
    with pytest.raises(ValueError):
        random_flow_network(n_layers, random.Random(1))


def test_random_weights_range():
    graph = DiGraph([(1, 2), (2, 3), (1, 3)])
    assert set(random_weights(graph, 3, 3, random.Random(1)).values()) == {3}
    with pytest.raises(ValueError):
        random_weights(graph, 10, 1, random.Random(1))
