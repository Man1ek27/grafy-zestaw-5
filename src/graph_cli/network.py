"""Sieć przepływowa: digraf, przepustowości i warstwy wierzchołków.

Wierzchołki mają numery 1..n: źródło s = 1, ujście t = n (tak numeruje je
generator z zadania 1 i tak czytamy sieć z pliku).
"""

import math
from dataclasses import dataclass

from networkx import DiGraph

from .parser import parse_weighted_arcs
from .shortest_paths import Weights, bfs


@dataclass
class FlowNetwork:
    """layers[0] = [s], layers[-1] = [t], pomiędzy warstwy pośrednie 1..N."""

    graph: DiGraph
    capacity: Weights
    layers: list[list[int]]

    @property
    def source(self) -> int:
        return self.layers[0][0]

    @property
    def sink(self) -> int:
        return self.layers[-1][0]


def check_flow_network(graph: DiGraph, capacity: Weights, s: int, t: int) -> None:
    """Warunki sieci z zadania 1; naruszenie kończy się ValueError.

    Łuki przeciwne u -> v i v -> u są zabronione jak w definicji sieci
    przepływowej (Cormen) — przy nich wzór (1) na c_f z alg_5.pdf byłby
    niejednoznaczny.
    """
    if graph.number_of_nodes() < 2:
        raise ValueError("Sieć musi mieć co najmniej 2 wierzchołki (s i t).")
    for u, v in sorted(graph.edges()):
        if capacity[(u, v)] < 1:
            raise ValueError(f"Przepustowość łuku ({u}, {v}) musi być dodatnia.")
        if v == s:
            raise ValueError(f"Łuk ({u}, {v}) wchodzi do źródła s = {s}.")
        if u == t:
            raise ValueError(f"Łuk ({u}, {v}) wychodzi z ujścia t = {t}.")
        if graph.has_edge(v, u):
            raise ValueError(f"Łuki przeciwne ({u}, {v}) i ({v}, {u}) są zabronione.")


def layers_from_bfs(graph: DiGraph, s: int, t: int) -> list[list[int]]:
    """Warstwy sieci wczytanej z pliku: warstwa v = liczba łuków od s (BFS).

    Ujście zawsze jest w ostatniej warstwie; wierzchołki nieosiągalne z s
    trafiają do osobnej warstwy tuż przed ujściem.
    """
    ds, _ = bfs(graph, s)
    inner = [v for v in sorted(graph.nodes()) if v not in (s, t)]
    last = max((ds[v] for v in inner if ds[v] != math.inf), default=0)

    layers = [[s]] + [[] for _ in range(last)]
    unreachable = []
    for v in inner:
        if ds[v] == math.inf:
            unreachable.append(v)
        else:
            layers[ds[v]].append(v)
    if unreachable:
        layers.append(unreachable)
    layers.append([t])
    return layers


def parse_flow_network(text: str) -> FlowNetwork:
    """Plik „n, potem linie u v c” (format z zestawu 4): s = 1, t = n."""
    graph, capacity = parse_weighted_arcs(text)
    n = graph.number_of_nodes()
    check_flow_network(graph, capacity, 1, n)
    return FlowNetwork(graph, capacity, layers_from_bfs(graph, 1, n))


def vertex_names(network: FlowNetwork) -> dict[int, str]:
    """Etykiety do wypisywania i rysowania: „s”, „t”, a pozostałe to numery."""
    names = {v: str(v) for v in network.graph.nodes()}
    names[network.source] = "s"
    names[network.sink] = "t"
    return names
