import random

import pytest
from networkx import DiGraph

from graph_cli.ford_fulkerson import (
    flow_value,
    ford_fulkerson,
    residual_capacity,
    residual_network,
)
from graph_cli.generators import random_flow_network
from helpers import FIGURE_2_FLOW, load, reference_max_flow


def run(network):
    flow, steps = ford_fulkerson(
        network.graph, network.capacity, network.source, network.sink
    )
    return flow, steps, flow_value(network.graph, flow, network.source)


def test_figure_2_of_input_5():
    flow, _, value = run(load("input-5.txt"))
    assert value == 19
    assert flow == FIGURE_2_FLOW


def test_figure_2_needs_cancelling_flow():
    _, steps, _ = run(load("input-5.txt"))
    assert [len(step.path) - 1 for step in steps] == [4, 4, 4, 4, 4, 7]
    assert steps[-1].path == [1, 4, 5, 2, 3, 7, 8, 11]
    assert steps[-1].capacity == 5
    assert steps[-1].cancelled == [(2, 5)]
    assert all(not step.cancelled for step in steps[:-1])


def test_augmenting_paths_never_get_shorter():
    for seed in range(50):
        _, steps, _ = run(random_flow_network(4, random.Random(seed)))
        lengths = [len(step.path) for step in steps]
        assert lengths == sorted(lengths)


def test_cormen_example():
    _, _, value = run(load("cormen-6.txt"))
    assert value == 23


def test_residual_capacity_formula():
    graph = DiGraph([(1, 2)])
    capacity = {(1, 2): 7}
    flow = {(1, 2): 3}
    assert residual_capacity(graph, capacity, flow, 1, 2) == 4
    assert residual_capacity(graph, capacity, flow, 2, 1) == 3
    graph.add_node(3)
    assert residual_capacity(graph, capacity, flow, 1, 3) == 0


def test_residual_network_skips_zero_capacities():
    graph = DiGraph([(1, 2), (2, 3)])
    capacity = {(1, 2): 5, (2, 3): 2}
    residual, cf = residual_network(graph, capacity, {(1, 2): 2, (2, 3): 2})
    assert cf == {(1, 2): 3, (2, 1): 2, (3, 2): 2}
    assert set(residual.edges()) == set(cf)


def test_no_path_gives_zero_flow():
    graph = DiGraph([(1, 2)])
    graph.add_node(3)
    flow, steps = ford_fulkerson(graph, {(1, 2): 4}, 1, 3)
    assert flow == {(1, 2): 0} and steps == []


def test_same_source_and_sink():
    with pytest.raises(ValueError):
        ford_fulkerson(DiGraph([(1, 2)]), {(1, 2): 1}, 1, 1)


@pytest.mark.parametrize("n_layers", [2, 3, 4, 5])
def test_random_networks_against_reference(n_layers):
    for seed in range(100):
        network = random_flow_network(n_layers, random.Random(seed))
        flow, _, value = run(network)
        graph, s, t = network.graph, network.source, network.sink

        # ograniczenia przepustowości
        for arc in graph.edges():
            assert 0 <= flow[arc] <= network.capacity[arc]
        # zachowanie przepływu w wierzchołkach pośrednich
        for v in graph.nodes():
            if v not in (s, t):
                into = sum(flow[(u, v)] for u in graph.predecessors(v))
                out = sum(flow[(v, w)] for w in graph.successors(v))
                assert into == out
        # do ujścia wpływa tyle, ile wypływa ze źródła
        assert sum(flow[(u, t)] for u in graph.predecessors(t)) == value
        assert value == reference_max_flow(network)
