# Graph CLI — Zestaw 5

Aplikacja CLI w Pythonie do sieci przepływowych: losowanie sieci warstwowej
między jednym źródłem s i jednym ujściem t (z przepustowościami z przedziału
[1, 10]), jej zakodowanie i narysowanie oraz wyznaczenie maksymalnego przepływu
algorytmem Forda-Fulkersona ze ścieżkami powiększającymi o najmniejszej liczbie
łuków (BFS, wariant Edmondsa-Karpa). Wierzchołki są numerowane od 1 do n:
źródło s = 1, ujście t = n.

NetworkX (`DiGraph`) przechowuje wierzchołki i łuki; algorytmy z zadań
(generator sieci, BFS, sieć rezydualna, Ford-Fulkerson) zaimplementowano
samodzielnie zgodnie z pseudokodem z `alg_5.pdf`. Matplotlib zapisuje rysunki PNG.

**Kod z poprzednich zestawów:** `init()` i `shortest_path()` (`shortest_paths.py`),
`random_weights()` (`generators.py`, tu losuje przepustowości), `parse_weighted_arcs()`
(`parser.py`) i `serialize_weighted_arcs()` (`serial.py`) — format pliku „u v waga”,
`draw_digraph()` z `label_position()` i `circle_positions()` (`visualization.py`),
funkcje `write_text()` i `print_table()`, schemat `cli.py` (`build_parser()`,
`COMMANDS`, `main()`), plik `__main__.py` i skrypt `scripts/fix_local_import.py`
pochodzą z zestawów 1–4. `draw_digraph()` uzupełniono o własne położenia
wierzchołków (warstwy), etykiety s/t, omijanie wierzchołków przez łuki i
rozsuwanie etykiet.

## 1. Przygotowanie środowiska

Wymagania: Python 3.10 lub nowszy. Git jest potrzebny do commitów i hooków.

```bash
git clone https://github.com/Man1ek27/grafy-zestaw-5.git
cd grafy-zestaw-5
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pre-commit install
```

Windows (Git Bash): `source .venv/Scripts/activate` zamiast `Activate.ps1`.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pre-commit install
```

Instalacja dodaje komendę `graph-cli`, biblioteki NetworkX i Matplotlib oraz
narzędzia developerskie Ruff, pre-commit i pytest. Jeżeli na macOS wystąpi
`ModuleNotFoundError: No module named 'graph_cli'`, wykonaj
`.venv/bin/python scripts/fix_local_import.py` (opis w README zestawu 1).

Alternatywne uruchomienie aplikacji: `python -m graph_cli`.

## 2. Dane wejściowe

- Oba polecenia przyjmują `--layers N` (losowa sieć z N ≥ 2 warstwami
  pośrednimi, procedura z zadania 1) albo `--input PLIK` z siecią zapisaną jako
  „lista łuków z wagami” z zestawu 4 (n, potem linie `u v c`), gdzie s = 1, t = n.
- `--seed` pozwala odtworzyć losowanie; ten sam `--seed` i `--layers` dają tę samą
  sieć w obu poleceniach. `--output PLIK` zapisuje sieć w formacie `--input`.

Formaty plików i wyjścia opisuje [docs/formats.md](docs/formats.md).

Przykłady w `examples/`:

| Plik            | Opis                                                                    |
| --------------- | ----------------------------------------------------------------------- |
| `input-5.txt`   | sieć z rys. 1 w input_5.pdf (N = 3; a..i = 2..10, t = 11), wynik: rys. 2, \|f_max\| = 19 |
| `cormen-6.txt`  | sieć z podręcznika Cormena (s, v1..v4, t = 1..6), \|f_max\| = 23        |

## 3. Wywołania CLI

Pomoc: `graph-cli --help`, `graph-cli ford-fulkerson --help` itd.

W obu poleceniach `--plot PLIK.png` zapisuje rysunek, a `--show`
(wymaga `--plot`) otwiera okno.

### Zadanie 1: losowa sieć przepływowa

```bash
graph-cli network --layers 3 --seed 1 --plot output/z1.png --output output/z1.txt
graph-cli network --input examples/input-5.txt --plot output/rys1.png
```

```text
Wylosowano sieć przepływową dla N = 3 warstw pośrednich.
Sieć: n = 9, m = 18, źródło s = 1, ujście t = 9
Warstwy:
0: s
1: 2 3
2: 4 5
3: 6 7 8
4: t
Łuki i przepustowości:
u  v  c(u,v)
s  2       1
s  3       1
2  3       1
...
Macierz przepustowości (wiersz u, kolumna v, 0 = brak łuku):
   s  2  3  4  5  6  7  8  t
s  0  1  1  0  0  0  0  0  0
...
```

Sieć jest zakodowana jako lista łuków z przepustowościami i jako macierz
przepustowości. Na rysunku warstwy są kolumnami od s (z lewej) do t (z prawej),
s i t mają inny kolor, a liczby na łukach to przepustowości c(u, v). Łuk, który
narysowany prosto przeszedłby przez inny wierzchołek, jest wygięty.

### Zadanie 2: maksymalny przepływ (Ford-Fulkerson)

```bash
graph-cli ford-fulkerson --input examples/input-5.txt --steps --plot output/z2.png
graph-cli ford-fulkerson --layers 3 --seed 1 --plot output/z2-losowa.png
```

```text
Ścieżki powiększające (BFS w sieci rezydualnej, najmniej łuków):
1) s -> 2 -> 5 -> 9 -> t, c_f(p) = 5
2) s -> 2 -> 6 -> 10 -> t, c_f(p) = 5
3) s -> 3 -> 6 -> 10 -> t, c_f(p) = 2
4) s -> 3 -> 7 -> 8 -> t, c_f(p) = 1
5) s -> 4 -> 7 -> 8 -> t, c_f(p) = 1
6) s -> 4 -> 5 -> 2 -> 3 -> 7 -> 8 -> t, c_f(p) = 5, cofnięto przepływ na łuku 2 -> 5
Liczba ścieżek powiększających: 6
Przepływ na łukach f(u,v)/c(u,v):
 u   v    f/c
 s   2  10/10
 ...
Wartość maksymalnego przepływu |f_max| = 19
```

`--steps` wypisuje kolejne ścieżki powiększające z c_f(p); krok 5 → 2 to łuk
przeciwny w sieci rezydualnej, czyli cofnięcie przepływu na łuku 2 → 5 (uwaga
z input_5.pdf). Wynik dla `input-5.txt` jest identyczny z rys. 2. Na rysunku
etykiety łuków to f(u, v)/c(u, v), a łuki z dodatnim przepływem są czerwone.

Sukces kończy program kodem 0; błędy danych lub plików kodem 1; błędne argumenty
CLI kodem 2. Komunikaty błędów trafiają na stderr.

## 4. Funkcje w kolejności wywoływania

### Wspólny początek

1. `main(argv=None)` w `cli.py` jest punktem wejścia komendy `graph-cli`.
2. `build_parser()` tworzy parser argparse; `add_network_arguments()`
   i `add_plot_arguments()` dodają wspólne opcje.
3. `main()` sprawdza zależność `--show` od `--plot` i wywołuje funkcję
   `run_*` z tablicy `COMMANDS`. `ValueError` i `OSError` kończą program kodem 1.
4. Każde `run_*` tworzy jeden generator `random.Random(seed)` i wywołuje
   `load_network()`: `parse_flow_network()` z `network.py` (czyli
   `parse_weighted_arcs()`, `check_flow_network()` i `layers_from_bfs()`) albo
   `random_flow_network()` z `generators.py`; `--output` → `serialize_weighted_arcs()`
   i `write_text()`.

### network (zad. 1)

`random_flow_network(N, rng)` w `generators.py`: `random_layers()` (warstwy
po 2..N wierzchołków), `connect_layers()` dla i = 0..N, `add_random_arcs()`
(2N łuków), `random_weights(graph, 1, 10, rng)` i kontrolne `check_flow_network()`.
Potem `run_network()` → `print_layers()`, tabela łuków (`print_table()`),
`print_capacity_matrix()` i `draw_flow_network()` (→ `layer_positions()`,
`draw_digraph()`).

### ford-fulkerson (zad. 2)

`run_ford_fulkerson()` → `ford_fulkerson(graph, capacity, s, t)` w
`ford_fulkerson.py`: zerowanie f, a w pętli `residual_network()` (wzór (1)
w `residual_capacity()`), `bfs(G_f, s, t)` z `shortest_paths.py` (kończy się
po dotarciu do t), `shortest_path(ps, t)`, c_f(p) i powiększenie przepływu.
Wartość |f| liczy `flow_value()`. Z `--steps` `print_augmenting_paths()`.

## 5. Formatowanie i testy

Ruff automatycznie formatuje pliki Pythona przy `git commit`.

```bash
ruff format .
ruff format --check .
pytest
```

Testy w `tests/` sprawdzają m.in. przykład z input_5.pdf (warstwy z rys. 1,
przepływ na każdym łuku z rys. 2, |f_max| = 19 i cofnięcie przepływu w ostatniej
iteracji), sieć z podręcznika Cormena (23), wszystkie warunki z treści zadania 1
dla kilkuset losowych sieci (rozmiary warstw, łuki między warstwami, 2N dodatkowych
łuków, brak łuków do s i z t, przepustowości z [1, 10]), BFS, wzór (1), błędne
pliki oraz zgodność |f_max| z niezależnym wzorcem (`networkx.maximum_flow_value`,
algorytm push-relabel) wraz z ograniczeniami przepustowości i zachowaniem
przepływu na kilkuset losowych sieciach.

## 6. Zakres i ograniczenia

- Generator nie dodaje łuku v → u, jeśli istnieje już łuk u → v. Treść zadania
  zabrania tylko łuków powtórzonych, ale sieć przepływowa w definicji z podręcznika
  Cormena (na którym oparto alg_5.pdf) nie ma łuków przeciwnych, a wzór (1) na
  c_f(u, v) bez tego założenia byłby niejednoznaczny. Plik z łukami przeciwnymi
  kończy się błędem.
- Sieć z pliku nie zawiera warstw, więc program wyznacza je BFS-em: warstwa
  wierzchołka to liczba łuków od s, t jest zawsze w ostatniej warstwie,
  a wierzchołki nieosiągalne z s — w osobnej warstwie przed t.
- Program przyjmuje dowolne N ≥ 2, ale rysunek jest czytelny dla N ≤ 4
  (tak jak zakłada treść zadania).
- Sieć rezydualna jest budowana od nowa w każdej iteracji, jak w pseudokodzie:
  iteracja O(n + m), liczba iteracji wariantu Edmondsa-Karpa O(n·m),
  łącznie O(n·m²).

Opis algorytmów i złożoności: [docs/algorithms.md](docs/algorithms.md).
Formaty wejścia i wyjścia: [docs/formats.md](docs/formats.md).
