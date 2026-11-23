"""Najkrótsze ścieżki z jednego źródła mierzone liczbą łuków: BFS (zadanie 2).

init i shortest_path pochodzą z zestawu 4 (init to algorytm pomocniczy
z alg_3.pdf). Wagi i przepustowości trzymamy w słowniku weights[(u, v)]
— odpowiednik macierzy w[u][v] z pseudokodu.
"""

import math
from collections import deque

from networkx import DiGraph

Weights = dict[tuple[int, int], int]


def init(graph: DiGraph, s: int) -> tuple[dict, dict]:
    """ds[v] = ∞ i ps[v] = NIL (None) dla każdego v, a potem ds[s] = 0."""
    ds = {}
    ps = {}
    for v in graph.nodes():
        ds[v] = math.inf
        ps[v] = None
    ds[s] = 0
    return ds, ps


def bfs(graph: DiGraph, s: int, t: int | None = None) -> tuple[dict, dict]:
    """Algorytm 2 z alg_5.pdf (przeszukiwanie wszerz). Zwraca (ds, ps).

    ds[v] to liczba łuków najkrótszej ścieżki s -> v, ps[v] poprzednik na niej.
    Jeśli podano t, przeszukiwanie kończy się zaraz po dotarciu do t — tak
    jak dopuszcza uwaga pod algorytmem (wystarcza nam ścieżka s -> t).
    """
    ds, ps = init(graph, s)  # linia 1
    queue = deque([s])  # linie 2–3
    while queue:  # linia 4
        v = queue.popleft()  # linia 5
        for u in sorted(graph.successors(v)):  # linia 6: łuki v -> u
            if ds[u] == math.inf:  # linie 7–10
                ds[u] = ds[v] + 1
                ps[u] = v
                queue.append(u)
                if u == t:
                    return ds, ps
    return ds, ps


def shortest_path(ps: dict, v: int) -> list[int]:
    """Odtwarza ścieżkę ze źródła do v, idąc po poprzednikach ps od końca."""
    path = []
    current = v
    while current is not None:
        path.append(current)
        current = ps[current]
    path.reverse()
    return path
