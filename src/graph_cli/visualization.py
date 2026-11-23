"""Rysowanie digrafu (kod z zestawów 1–4) i sieci przepływowej w warstwach.

draw_digraph pochodzi z zestawu 4; w zestawie 5 przyjmuje dodatkowo położenia
wierzchołków (warstwy zamiast okręgu), ich etykiety (s, t) i rozmiar rysunku,
a łuk przechodzący przez inny wierzchołek rysuje jako wygięty.
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
from networkx import DiGraph

# wygięcie łuku, gdy istnieją oba łuki u -> v i v -> u (inaczej by się nakładały)
CURVE = 0.2
# wygięcie łuku, który narysowany prosto przeszedłby przez inny wierzchołek
AVOID_CURVE = 0.3
AVOID_DISTANCE = 0.2
NODE_SIZE = 500
ARROW_SHRINK = 13  # strzałka kończy się na brzegu kółka wierzchołka
LAYER_GAP = 1.6  # odległość między kolejnymi warstwami sieci
ROW_GAP = 1.2  # odległość między wierzchołkami w jednej warstwie
LABEL_GAP = 0.3  # minimalna odległość między etykietami łuków
LABEL_NODE_GAP = 0.2  # etykieta nie może zasłaniać kółka wierzchołka

Position = tuple[float, float]


def circle_positions(nodes: list[int]) -> dict[int, Position]:
    """Wierzchołek 1 u góry, kolejne zgodnie z ruchem wskazówek zegara."""
    positions = {}
    for i, node in enumerate(nodes):
        angle = math.pi / 2 - 2 * math.pi * i / len(nodes)
        positions[node] = (math.cos(angle), math.sin(angle))
    return positions


def layer_positions(layers: list[list[int]]) -> dict[int, Position]:
    """Warstwa i to kolumna x = i · LAYER_GAP; w kolumnie wierzchołki od góry.

    Jak na rys. 1 w input_5.pdf wierzchołki są lekko przesunięte w pionie
    (nieregularnie), żeby etykiety łuków rzadziej się nakładały.
    """
    positions = {}
    for i, layer in enumerate(layers):
        size = len(layer)
        for j, v in enumerate(layer):
            shift = 0.3 * ((i + j) % 3 - 1) if size > 1 else 0.0
            positions[v] = (i * LAYER_GAP, ((size - 1) / 2 - j) * ROW_GAP + shift)
    return positions


def label_position(
    start: Position, end: Position, curve: float, t: float = 0.5
) -> Position:
    """Punkt łuku narysowanego stylem arc3 z wygięciem curve (t = 0.5 to środek).

    Matplotlib rysuje go jako krzywą Béziera z punktem kontrolnym
    środek + curve · (dy, −dx); punkt krzywej dla parametru t to
    (1 − t)² · start + 2t(1 − t) · kontrolny + t² · koniec.
    """
    (x1, y1), (x2, y2) = start, end
    control_x = (x1 + x2) / 2 + curve * (y2 - y1)
    control_y = (y1 + y2) / 2 - curve * (x2 - x1)
    a, b, c = (1 - t) ** 2, 2 * t * (1 - t), t**2
    return a * x1 + b * control_x + c * x2, a * y1 + b * control_y + c * y2


def free_label_position(
    start: Position,
    end: Position,
    curve: float,
    label_at: float,
    taken: list[Position],
    nodes: list[Position],
) -> Position:
    """Pierwsze miejsce na łuku (zaczynając od label_at), gdzie etykieta nie
    nachodzi na wcześniejsze etykiety (taken) ani na kółka wierzchołków.

    Gdy takiego miejsca nie ma, wybiera punkt najdalszy od innych etykiet.
    """
    best, best_distance = None, -1.0
    for shift in (0, -0.1, 0.1, -0.2, 0.15, -0.25, 0.25):
        x, y = label_position(start, end, curve, label_at + shift)
        if any(math.hypot(x - nx, y - ny) < LABEL_NODE_GAP for nx, ny in nodes):
            continue
        # etykieta jest szersza niż wyższa, więc odległość w pionie liczy się 2×
        distance = min(
            (max(abs(x - lx), 2 * abs(y - ly)) for lx, ly in taken), default=math.inf
        )
        if distance >= LABEL_GAP:
            return x, y
        if distance > best_distance:
            best, best_distance = (x, y), distance
    return best or label_position(start, end, curve, label_at)


def passes_near_vertex(
    u: int, v: int, positions: dict[int, Position], distance: float = AVOID_DISTANCE
) -> bool:
    """Czy odcinek u -> v przechodzi blisko innego wierzchołka (np. w tej samej kolumnie)."""
    (x1, y1), (x2, y2) = positions[u], positions[v]
    dx, dy = x2 - x1, y2 - y1
    length2 = dx * dx + dy * dy
    for w, (x, y) in positions.items():
        if w in (u, v) or length2 == 0:
            continue
        # rzut punktu w na odcinek: t = 0 w u, t = 1 w v
        t = ((x - x1) * dx + (y - y1) * dy) / length2
        if 0 < t < 1 and math.hypot(x1 + t * dx - x, y1 + t * dy - y) < distance:
            return True
    return False


def draw_digraph(
    graph: DiGraph,
    output: Path,
    show: bool = False,
    colors: dict[int, int] | None = None,
    weights: dict[tuple[int, int], int | str] | None = None,
    highlight: set[tuple[int, int]] | None = None,
    title: str = "Digraf",
    positions: dict[int, Position] | None = None,
    names: dict[int, str] | None = None,
    figsize: tuple[float, float] = (7, 7),
    label_at: float = 0.5,
) -> None:
    """Zapisuje rysunek digrafu do pliku PNG.

    colors przypisuje wierzchołkowi numer grupy (kolor), weights to etykiety
    łuków (wagi, przepustowości albo „f/c”), a łuki z highlight są czerwone.
    positions domyślnie układa wierzchołki na okręgu, names zastępuje numery
    na kółkach, a label_at mówi, w którym miejscu łuku stoi etykieta.
    """
    nodes = sorted(graph.nodes())
    positions = positions or circle_positions(nodes)
    names = names or {}
    highlight = highlight or set()
    palette = plt.get_cmap("tab10").colors

    plt.figure(figsize=figsize)
    plt.axis("off")
    plt.title(title)

    taken = []  # miejsca już narysowanych etykiet łuków
    for u, v in sorted(graph.edges()):
        if graph.has_edge(v, u):
            curve = CURVE
        elif passes_near_vertex(u, v, positions):
            curve = AVOID_CURVE
        else:
            curve = 0.0
        color = "red" if (u, v) in highlight else "black"
        plt.annotate(
            "",
            xy=positions[v],
            xytext=positions[u],
            arrowprops={
                "arrowstyle": "-|>",
                "color": color,
                "lw": 1.8 if color == "red" else 1.0,
                "shrinkA": ARROW_SHRINK,
                "shrinkB": ARROW_SHRINK,
                "connectionstyle": f"arc3,rad={curve}",
            },
            zorder=1,
        )
        if weights is not None:
            x, y = free_label_position(
                positions[u],
                positions[v],
                curve,
                label_at,
                taken,
                list(positions.values()),
            )
            taken.append((x, y))
            plt.text(
                x,
                y,
                str(weights[(u, v)]),
                fontsize=9,
                ha="center",
                va="center",
                color=color,
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none"},
                zorder=3,
            )

    for node, (x, y) in positions.items():
        node_color = palette[(colors[node] - 1) % len(palette)] if colors else "blue"
        plt.scatter(x, y, s=NODE_SIZE, color=node_color, zorder=2)
        plt.text(
            x,
            y,
            names.get(node, str(node)),
            fontsize=12,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            zorder=4,
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    plt.gca().set_aspect("equal", adjustable="box")
    plt.margins(0.15)
    plt.savefig(output, bbox_inches="tight")
    if show:
        plt.show()

    plt.close()


def draw_flow_network(
    graph: DiGraph,
    layers: list[list[int]],
    labels: dict[tuple[int, int], int | str],
    output: Path,
    show: bool = False,
    names: dict[int, str] | None = None,
    highlight: set[tuple[int, int]] | None = None,
    title: str = "Sieć przepływowa",
) -> None:
    """Sieć w warstwach od lewej (s) do prawej (t); s i t mają inny kolor."""
    s, t = layers[0][0], layers[-1][0]
    colors = {v: 2 if v in (s, t) else 1 for v in graph.nodes()}
    height = max(len(layer) for layer in layers)
    figsize = (2.4 * len(layers) + 1, 1.8 * height + 1.5)
    draw_digraph(
        graph,
        output,
        show,
        colors=colors,
        weights=labels,
        highlight=highlight,
        title=title,
        positions=layer_positions(layers),
        names=names,
        figsize=figsize,
        label_at=0.4,
    )
