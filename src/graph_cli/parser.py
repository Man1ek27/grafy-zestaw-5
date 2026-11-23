"""Parsowanie digrafu z wagami (kod z zestawu 4); w zestawie 5 wagą jest przepustowość."""

from networkx import DiGraph


# WEIGHTED ARCS -> DIGRAPH + WAGI
def parse_weighted_arcs(text: str) -> tuple[DiGraph, dict[tuple[int, int], int]]:
    """Pierwsza linia: n; każda kolejna niepusta linia: „u v waga” (łuk u -> v)."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Pusty plik — brak liczby wierzchołków.")

    nodes = int(lines[0])
    if nodes < 0:
        raise ValueError("Liczba wierzchołków nie może być ujemna.")

    graph = DiGraph()
    graph.add_nodes_from(range(1, nodes + 1))
    weights = {}
    for line in lines[1:]:
        values = list(map(int, line.split()))
        if len(values) != 3:
            raise ValueError(f"Linia „{line}” musi mieć postać: u v waga.")

        u, v, weight = values
        if not (1 <= u <= nodes and 1 <= v <= nodes):
            raise ValueError(f"Łuk ({u}, {v}) ma wierzchołek spoza zakresu 1-{nodes}.")
        if u == v:
            raise ValueError(f"Digraf prosty nie ma pętli ({u}).")
        if graph.has_edge(u, v):
            raise ValueError(f"Powtórzony łuk: ({u}, {v}).")

        graph.add_edge(u, v)
        weights[(u, v)] = weight
    return graph, weights
