import pytest

from graph_cli.cli import main
from graph_cli.network import parse_flow_network
from helpers import EXAMPLES


def run(capsys, *argv):
    code = main([str(arg) for arg in argv])
    return code, capsys.readouterr().out


def run_error(capsys, *argv):
    with pytest.raises(SystemExit) as error:
        main([str(arg) for arg in argv])
    return error.value.code, capsys.readouterr().err


def test_network_random_prints_draws_and_saves(capsys, tmp_path):
    path = tmp_path / "net.txt"
    code, out = run(
        capsys,
        "network",
        "--layers",
        3,
        "--seed",
        1,
        "--output",
        path,
        "--plot",
        tmp_path / "net.png",
    )
    assert code == 0
    assert "Wylosowano sieć przepływową dla N = 3 warstw pośrednich." in out
    assert "Łuki i przepustowości:" in out
    assert "Macierz przepustowości" in out
    assert (tmp_path / "net.png").exists()
    network = parse_flow_network(path.read_text(encoding="utf-8"))
    assert network.graph.number_of_edges() > 0


def test_network_from_file(capsys):
    _, out = run(capsys, "network", "--input", EXAMPLES / "input-5.txt")
    assert "Warstwy:\n0: s\n1: 2 3 4\n2: 5 6 7\n3: 8 9 10\n4: t\n" in out
    assert " s  0  10  3  6" in out


def test_ford_fulkerson_figure_2(capsys, tmp_path):
    code, out = run(
        capsys,
        "ford-fulkerson",
        "--input",
        EXAMPLES / "input-5.txt",
        "--steps",
        "--plot",
        tmp_path / "ff.png",
    )
    assert code == 0
    assert "1) s -> 2 -> 5 -> 9 -> t, c_f(p) = 5\n" in out
    assert "cofnięto przepływ na łuku 2 -> 5" in out
    assert " s   2  10/10\n" in out
    assert out.endswith("Wartość maksymalnego przepływu |f_max| = 19\n")
    assert (tmp_path / "ff.png").exists()


def test_same_seed_gives_the_same_network_in_both_commands(capsys, tmp_path):
    run(capsys, "network", "--layers", 4, "--seed", 9, "--output", tmp_path / "a.txt")
    run(
        capsys,
        "ford-fulkerson",
        "--layers",
        4,
        "--seed",
        9,
        "--output",
        tmp_path / "b.txt",
    )
    first = (tmp_path / "a.txt").read_text(encoding="utf-8")
    assert first == (tmp_path / "b.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "argv",
    [
        ["network", "--layers", 1],
        ["ford-fulkerson", "--layers", 0],
        ["ford-fulkerson", "--input", EXAMPLES / "brak.txt"],
    ],
)
def test_errors_exit_with_code_1(capsys, argv):
    code, err = run_error(capsys, *argv)
    assert code == 1
    assert err.startswith("Błąd: ")


def test_invalid_network_file(capsys, tmp_path):
    path = tmp_path / "bad.txt"
    path.write_text("3\n1 2 4\n2 1 4\n2 3 1\n", encoding="utf-8")
    code, err = run_error(capsys, "ford-fulkerson", "--input", path)
    assert code == 1 and "przeciwne" in err


def test_show_requires_plot(capsys):
    code, _ = run_error(capsys, "network", "--layers", 3, "--show")
    assert code == 2


def test_input_and_layers_are_exclusive(capsys):
    code, _ = run_error(
        capsys, "network", "--input", EXAMPLES / "input-5.txt", "--layers", 3
    )
    assert code == 2
