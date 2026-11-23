"""Losowa sieć przepływowa z warstwami (zadanie 1).

random_weights to kod z zestawu 4 — tu losuje przepustowości z [1, 10].
Funkcje przyjmują generator rng = random.Random(seed), żeby losowanie
dało się powtórzyć.
"""

import random

from networkx import DiGraph

from .network import FlowNetwork, check_flow_network
from .shortest_paths import Weights

CAPACITY_RANGE = (1, 10)


def random_weights(graph: DiGraph, low: int, high: int, rng: random.Random) -> Weights:
    """Każdy łuk dostaje losową całkowitą wagę z przedziału [low, high]."""
    if low > high:
        raise ValueError("Dolna granica wag nie może być większa od górnej.")

    weights = {}
    for u, v in sorted(graph.edges()):
        weights[(u, v)] = rng.randint(low, high)
    return weights


def random_flow_network(layers_count: int, rng: random.Random) -> FlowNetwork:
    """Sieć według procedury z zadania 1 dla N = layers_count warstw pośrednich."""
    if layers_count < 2:
        raise ValueError("Liczba warstw pośrednich N musi wynosić co najmniej 2.")

    layers = random_layers(layers_count, rng)
    graph = DiGraph()
    for layer in layers:
        graph.add_nodes_from(layer)

    for i in range(len(layers) - 1):  # i = 0, ..., N
        connect_layers(graph, layers[i], layers[i + 1], rng)

    s, t = layers[0][0], layers[-1][0]
    add_random_arcs(graph, 2 * layers_count, s, t, rng)

    capacity = random_weights(graph, *CAPACITY_RANGE, rng)
    check_flow_network(graph, capacity, s, t)
    return FlowNetwork(graph, capacity, layers)


def random_layers(layers_count: int, rng: random.Random) -> list[list[int]]:
    """Warstwa 0 = [s], potem N warstw po 2..N wierzchołków, na końcu [t].

    Wierzchołki są numerowane kolejno warstwami: s = 1, ..., t = n.
    """
    layers = [[1]]
    next_vertex = 2
    for _ in range(layers_count):
        size = rng.randint(2, layers_count)
        layers.append(list(range(next_vertex, next_vertex + size)))
        next_vertex += size
    layers.append([next_vertex])
    return layers


def connect_layers(
    graph: DiGraph, layer: list[int], next_layer: list[int], rng: random.Random
) -> None:
    """Łuki z warstwy i do i + 1: z każdego u wychodzi i do każdego v wchodzi łuk."""
    # każdy wierzchołek warstwy i dostaje łuk do losowego wierzchołka warstwy i + 1
    for u in layer:
        graph.add_edge(u, rng.choice(next_layer))

    # wierzchołki warstwy i + 1 bez łuku wchodzącego dostają go z losowego u
    for v in next_layer:
        if not any(graph.has_edge(u, v) for u in layer):
            graph.add_edge(rng.choice(layer), v)


def add_random_arcs(
    graph: DiGraph, count: int, s: int, t: int, rng: random.Random
) -> None:
    """Dodaje count łuków wylosowanych spośród wszystkich dozwolonych par (u, v).

    Kierunek nie musi zgadzać się z warstwami. Pomijamy pętle, łuki istniejące,
    łuki przeciwne do istniejących oraz łuki do s i z t.
    """
    for _ in range(count):
        candidates = [
            (u, v)
            for u in sorted(graph.nodes())
            for v in sorted(graph.nodes())
            if u != v
            and v != s
            and u != t
            and not graph.has_edge(u, v)
            and not graph.has_edge(v, u)
        ]
        if not candidates:
            raise ValueError("Brak wolnych par wierzchołków na kolejny łuk.")
        graph.add_edge(*rng.choice(candidates))
