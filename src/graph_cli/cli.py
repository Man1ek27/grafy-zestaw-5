"""Interfejs terminalowy; logika sieci przepływowych znajduje się w osobnych modułach.

Schemat (podkomendy, main, COMMANDS) oraz funkcje write_text i print_table
pochodzą z poprzednich zestawów.
"""

import argparse
import random
from pathlib import Path

from .ford_fulkerson import AugmentingPath, flow_value, ford_fulkerson
from .generators import random_flow_network
from .network import FlowNetwork, parse_flow_network, vertex_names
from .serial import serialize_weighted_arcs
from .visualization import draw_flow_network


def add_network_arguments(command: argparse.ArgumentParser) -> None:
    """Źródło sieci: plik (--input) albo losowa sieć z N warstwami (--layers N)."""
    source = command.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="plik z siecią (n, linie u v c)")
    source.add_argument(
        "--layers", type=int, metavar="N", help="losowa sieć z N warstwami pośrednimi"
    )
    command.add_argument("--seed", type=int)
    command.add_argument("--output", type=Path, help="zapis sieci (łuki z c)")


def add_plot_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--plot", type=Path)
    command.add_argument("--show", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sieci przepływowe — zestaw 5")
    commands = parser.add_subparsers(dest="command", required=True)

    network = commands.add_parser("network", help="Zad. 1: losowa sieć przepływowa")
    add_network_arguments(network)
    add_plot_arguments(network)

    ff = commands.add_parser(
        "ford-fulkerson", help="Zad. 2: maksymalny przepływ (Ford-Fulkerson)"
    )
    add_network_arguments(ff)
    ff.add_argument(
        "--steps", action="store_true", help="wypisz kolejne ścieżki powiększające"
    )
    add_plot_arguments(ff)
    return parser


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def print_table(rows: list[list]) -> None:
    """Wypisuje tabelę z kolumnami wyrównanymi do prawej."""
    texts = [[str(cell) for cell in row] for row in rows]

    # szerokość kolumny = najdłuższy tekst w tej kolumnie
    widths = []
    for column in range(len(texts[0])):
        widths.append(max(len(row[column]) for row in texts))

    for row in texts:
        cells = [cell.rjust(width) for cell, width in zip(row, widths)]
        print("  ".join(cells))


def load_network(args: argparse.Namespace, rng: random.Random) -> FlowNetwork:
    """Sieć z pliku (s = 1, t = n) albo wylosowana procedurą z zadania 1."""
    if args.input is not None:
        network = parse_flow_network(args.input.read_text(encoding="utf-8"))
    else:
        network = random_flow_network(args.layers, rng)
        print(f"Wylosowano sieć przepływową dla N = {args.layers} warstw pośrednich.")

    if args.output is not None:
        write_text(
            args.output, serialize_weighted_arcs(network.graph, network.capacity)
        )
    return network


def print_layers(network: FlowNetwork, names: dict[int, str]) -> None:
    graph = network.graph
    print(
        f"Sieć: n = {graph.number_of_nodes()}, m = {graph.number_of_edges()}, "
        f"źródło s = {network.source}, ujście t = {network.sink}"
    )
    print("Warstwy:")
    for i, layer in enumerate(network.layers):
        print(f"{i}: " + " ".join(names[v] for v in layer))


def print_capacity_matrix(network: FlowNetwork, names: dict[int, str]) -> None:
    """Macierz przepustowości: c[u][v] w wierszu u i kolumnie v, 0 = brak łuku."""
    nodes = sorted(network.graph.nodes())
    rows = [[""] + [names[v] for v in nodes]]
    for u in nodes:
        rows.append([names[u]] + [network.capacity.get((u, v), 0) for v in nodes])
    print_table(rows)


def run_network(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    network = load_network(args, rng)
    names = vertex_names(network)
    print_layers(network, names)

    print("Łuki i przepustowości:")
    rows = [["u", "v", "c(u,v)"]]
    for u, v in sorted(network.graph.edges()):
        rows.append([names[u], names[v], network.capacity[(u, v)]])
    print_table(rows)

    print("Macierz przepustowości (wiersz u, kolumna v, 0 = brak łuku):")
    print_capacity_matrix(network, names)

    if args.plot is not None:
        draw_flow_network(
            network.graph,
            network.layers,
            network.capacity,
            args.plot,
            args.show,
            names=names,
            title="Sieć przepływowa (przepustowości łuków)",
        )


def format_path(path: list[int], names: dict[int, str]) -> str:
    return " -> ".join(names[v] for v in path)


def print_augmenting_paths(steps: list[AugmentingPath], names: dict[int, str]) -> None:
    print("Ścieżki powiększające (BFS w sieci rezydualnej, najmniej łuków):")
    for nr, step in enumerate(steps, start=1):
        line = f"{nr}) {format_path(step.path, names)}, c_f(p) = {step.capacity}"
        if step.cancelled:
            arcs = ", ".join(f"{names[u]} -> {names[v]}" for u, v in step.cancelled)
            line += f", cofnięto przepływ na łuku {arcs}"
        print(line)


def run_ford_fulkerson(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    network = load_network(args, rng)
    names = vertex_names(network)
    print_layers(network, names)

    graph, capacity = network.graph, network.capacity
    flow, steps = ford_fulkerson(graph, capacity, network.source, network.sink)
    if args.steps:
        print_augmenting_paths(steps, names)
    print(f"Liczba ścieżek powiększających: {len(steps)}")

    print("Przepływ na łukach f(u,v)/c(u,v):")
    rows = [["u", "v", "f/c"]]
    for u, v in sorted(graph.edges()):
        rows.append([names[u], names[v], f"{flow[(u, v)]}/{capacity[(u, v)]}"])
    print_table(rows)

    value = flow_value(graph, flow, network.source)
    print(f"Wartość maksymalnego przepływu |f_max| = {value}")

    if args.plot is not None:
        labels = {arc: f"{flow[arc]}/{capacity[arc]}" for arc in graph.edges()}
        used = {arc for arc in graph.edges() if flow[arc] > 0}
        draw_flow_network(
            graph,
            network.layers,
            labels,
            args.plot,
            args.show,
            names=names,
            highlight=used,
            title=f"Maksymalny przepływ f/c, |f_max| = {value}",
        )


COMMANDS = {
    "network": run_network,
    "ford-fulkerson": run_ford_fulkerson,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.show and args.plot is None:
        parser.error("--show wymaga --plot.")
    try:
        COMMANDS[args.command](args)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Błąd: {error}\n")
    return 0
