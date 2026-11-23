"""Maksymalny przepływ algorytmem Forda-Fulkersona (zadanie 2).

Ścieżki powiększające to ścieżki o najmniejszej liczbie łuków w sieci
rezydualnej, wyszukiwane przez BFS (wariant Edmondsa-Karpa z alg_5.pdf).
Przepływ, jak przepustowości, trzymamy w słowniku flow[(u, v)].
"""

from dataclasses import dataclass

from networkx import DiGraph

from .shortest_paths import Weights, bfs, shortest_path

Flow = dict[tuple[int, int], int]


@dataclass
class AugmentingPath:
    """Jedna iteracja pętli while: ścieżka p, c_f(p) i łuki z cofniętym przepływem."""

    path: list[int]
    capacity: int
    cancelled: list[tuple[int, int]]


def residual_capacity(
    graph: DiGraph, capacity: Weights, flow: Flow, u: int, v: int
) -> int:
    """Wzór (1) z alg_5.pdf: przepustowość rezydualna c_f(u, v)."""
    if graph.has_edge(u, v):
        return capacity[(u, v)] - flow[(u, v)]
    if graph.has_edge(v, u):
        return flow[(v, u)]
    return 0


def residual_network(
    graph: DiGraph, capacity: Weights, flow: Flow
) -> tuple[DiGraph, Weights]:
    """Sieć rezydualna G_f: łuki (u, v) i (v, u) o dodatniej wartości c_f."""
    residual = DiGraph()
    residual.add_nodes_from(graph.nodes())
    cf = {}
    for u, v in sorted(graph.edges()):
        for a, b in ((u, v), (v, u)):
            value = residual_capacity(graph, capacity, flow, a, b)
            if value > 0:
                residual.add_edge(a, b)
                cf[(a, b)] = value
    return residual, cf


def ford_fulkerson(
    graph: DiGraph, capacity: Weights, s: int, t: int
) -> tuple[Flow, list[AugmentingPath]]:
    """Algorytm 1 z alg_5.pdf. Zwraca maksymalny przepływ f i kolejne ścieżki."""
    if s == t:
        raise ValueError("Źródło i ujście muszą być różnymi wierzchołkami.")

    # linie 1–3: zerowanie przepływów
    flow = {}
    for u, v in graph.edges():
        flow[(u, v)] = 0

    steps = []
    while True:
        # linia 4: najkrótsza (w łukach) ścieżka s -> t w G_f, szukana przez BFS
        residual, cf = residual_network(graph, capacity, flow)
        _, ps = bfs(residual, s, t)
        if ps[t] is None:
            break
        path = shortest_path(ps, t)
        arcs = list(zip(path, path[1:]))

        # linia 5: c_f(p) = najmniejsza przepustowość rezydualna na ścieżce
        cf_p = min(cf[arc] for arc in arcs)

        # linie 6–12: powiększenie przepływu wzdłuż p
        cancelled = []
        for u, v in arcs:
            if graph.has_edge(u, v):
                flow[(u, v)] += cf_p
            else:
                flow[(v, u)] -= cf_p  # kasowanie przepływu na łuku v -> u
                cancelled.append((v, u))
        steps.append(AugmentingPath(path, cf_p, cancelled))
    return flow, steps


def flow_value(graph: DiGraph, flow: Flow, s: int) -> int:
    """|f| = przepływ wychodzący ze źródła minus wchodzący do niego."""
    out_flow = sum(flow[(s, v)] for v in graph.successors(s))
    in_flow = sum(flow[(u, s)] for u in graph.predecessors(s))
    return out_flow - in_flow
