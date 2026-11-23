"""Eksport digrafu z wagami (kod z zestawu 4); w zestawie 5 wagą jest przepustowość."""

from networkx import DiGraph


# DIGRAPH + WAGI -> WEIGHTED ARCS
def serialize_weighted_arcs(graph: DiGraph, weights: dict[tuple[int, int], int]) -> str:
    """Format czytany przez parse_weighted_arcs: n, potem linie „u v waga”."""
    lines = [str(graph.number_of_nodes())]
    for u, v in sorted(graph.edges()):
        lines.append(f"{u} {v} {weights[(u, v)]}")
    return "\n".join(lines) + "\n"
