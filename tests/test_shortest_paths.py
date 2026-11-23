import math

from networkx import DiGraph

from graph_cli.shortest_paths import bfs, init, shortest_path


def digraph(n, arcs):
    graph = DiGraph()
    graph.add_nodes_from(range(1, n + 1))
    graph.add_edges_from(arcs)
    return graph


def test_init():
    ds, ps = init(digraph(3, []), 2)
    assert ds == {1: math.inf, 2: 0, 3: math.inf}
    assert ps == {1: None, 2: None, 3: None}


def test_bfs_counts_arcs_not_weights():
    # 1 -> 2 -> 3 -> 4 oraz skrót 1 -> 4
    graph = digraph(5, [(1, 2), (2, 3), (3, 4), (1, 4), (4, 5)])
    ds, ps = bfs(graph, 1)
    assert ds == {1: 0, 2: 1, 3: 2, 4: 1, 5: 2}
    assert shortest_path(ps, 5) == [1, 4, 5]


def test_bfs_follows_arc_directions():
    graph = digraph(3, [(2, 1), (2, 3)])
    ds, ps = bfs(graph, 1)
    assert ds[2] == math.inf and ds[3] == math.inf
    assert ps[3] is None


def test_bfs_stops_when_target_is_found():
    # sąsiedzi 1 to 2 i 3; po dotarciu do 2 przeszukiwanie się kończy
    graph = digraph(4, [(1, 2), (1, 3), (3, 4)])
    ds, ps = bfs(graph, 1, 2)
    assert ds[2] == 1 and ps[2] == 1
    assert ds[4] == math.inf  # 4 nie zostało już odwiedzone


def test_bfs_ties_are_broken_by_vertex_number():
    graph = digraph(4, [(1, 3), (1, 2), (2, 4), (3, 4)])
    _, ps = bfs(graph, 1)
    assert shortest_path(ps, 4) == [1, 2, 4]


def test_shortest_path_of_source():
    _, ps = bfs(digraph(2, [(1, 2)]), 1)
    assert shortest_path(ps, 1) == [1]
