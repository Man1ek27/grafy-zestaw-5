# Algorytmy i złożoność

Opis dotyczy aktualnej implementacji. n oznacza liczbę wierzchołków, m liczbę
łuków. Wierzchołki mają numery 1..n, źródło s = 1, ujście t = n. Digraf
przechowuje `networkx.DiGraph` (dodawanie łuków, następnicy, sprawdzenie łuku);
wszystkie algorytmy z zadań są zaimplementowane samodzielnie. Przepustowości
i przepływ są w słownikach `capacity[(u, v)]` i `flow[(u, v)]`, które odpowiadają
c(u, v) i f(u, v) z pseudokodu. Koszty zakładają stały oczekiwany czas operacji
na tablicach haszujących.

## 1. Losowa sieć przepływowa — `generators.py`

`random_flow_network(N, rng)` realizuje procedurę z treści zadania 1:

1. `random_layers(N, rng)` — warstwa 0 to [s], warstwy 1..N mają po
   `rng.randint(2, N)` wierzchołków, warstwa N + 1 to [t]. Wierzchołki są
   numerowane kolejno warstwami, więc s = 1 i t = n.
2. `connect_layers(graph, warstwa_i, warstwa_i+1, rng)` dla i = 0..N:
   - każdy u z warstwy i dostaje łuk do losowego v z warstwy i + 1
     (z każdego wierzchołka warstwy i wychodzi łuk);
   - każdy v z warstwy i + 1, do którego jeszcze nic nie wchodzi, dostaje łuk
     z losowego u z warstwy i (do każdego wierzchołka warstwy i + 1 wchodzi łuk).

   W szczególności s ma łuk do każdego wierzchołka warstwy 1, a każdy wierzchołek
   warstwy N ma łuk do t. Każdy wierzchołek leży więc na ścieżce s → t.
3. `add_random_arcs(graph, 2N, s, t, rng)` — 2N razy wybiera łuk równomiernie
   spośród wszystkich dozwolonych par (u, v), bez względu na warstwy. Para jest
   dozwolona, gdy u ≠ v, v ≠ s, u ≠ t i nie istnieje ani łuk u → v, ani v → u
   (uzasadnienie zakazu łuków przeciwnych w README, rozdz. 6).
4. `random_weights(graph, 1, 10, rng)` (z zestawu 4) — przepustowości
   `rng.randint(1, 10)`.
5. `check_flow_network()` sprawdza warunki sieci (kontrolnie).

Czas: warstwy i łuki między warstwami O(n²) w najgorszym razie, losowanie 2N łuków
O(N·n²) (lista kandydatów budowana od nowa przed każdym łukiem).

## 2. Sieć z pliku — `network.py`

`parse_flow_network(text)`: `parse_weighted_arcs()` (zestaw 4), potem
`check_flow_network(graph, capacity, 1, n)` — n ≥ 2, przepustowości ≥ 1, brak łuków
do s i z t, brak łuków przeciwnych — i `layers_from_bfs(graph, 1, n)`: warstwa
wierzchołka to ds[v] z `bfs(graph, s)`; t trafia do ostatniej warstwy,
nieosiągalne wierzchołki do osobnej warstwy przed t. Odległości BFS są kolejnymi
liczbami, więc żadna warstwa nie jest pusta. Czas O(n log n + m).

Dla sieci z rys. 1 w input_5.pdf warstwy z BFS są dokładnie warstwami z rysunku.

## 3. Przeszukiwanie wszerz — `shortest_paths.py`

`bfs(graph, s, t=None)` (algorytm 2 z `alg_5.pdf`):

1. `init(graph, s)` (z zestawu 4) — ds[v] = ∞, ps[v] = None, ds[s] = 0.
2. Kolejka Q = [s] (`collections.deque`).
3. Dopóki Q nie jest pusta: v = początek kolejki; dla każdego następnika u
   (w kolejności numerów), jeśli ds[u] = ∞: ds[u] = ds[v] + 1, ps[u] = v,
   u na koniec kolejki.
4. Jeśli podano t, funkcja kończy się, gdy tylko ds[t] zostanie ustawione —
   zgodnie z uwagą pod algorytmem.

ds[v] to liczba łuków najkrótszej ścieżki s → v. `shortest_path(ps, v)`
(z zestawu 4) odtwarza ścieżkę po poprzednikach. Czas O(n + m) plus sortowanie
następników.

## 4. Ford-Fulkerson — `ford_fulkerson.py`

`residual_capacity(graph, capacity, flow, u, v)` — wzór (1) z `alg_5.pdf`:

- c(u, v) − f(u, v), gdy (u, v) jest łukiem sieci,
- f(v, u), gdy (v, u) jest łukiem sieci (można cofnąć przepływ),
- 0 w przeciwnym razie.

`residual_network(graph, capacity, flow)` buduje G_f: dla każdego łuku (u, v)
sieci dodaje łuki (u, v) i (v, u) z dodatnią przepustowością rezydualną. Czas O(n + m).

`ford_fulkerson(graph, capacity, s, t)` (algorytm 1):

1. Linie 1–3: f(u, v) = 0 dla każdego łuku.
2. Linia 4: `residual_network()` i `bfs(G_f, s, t)`; gdy ps[t] = None, nie ma ścieżki
   powiększającej i przepływ jest maksymalny. W przeciwnym razie
   p = `shortest_path(ps, t)` — ścieżka o najmniejszej liczbie łuków
   (wariant Edmondsa-Karpa).
3. Linia 5: c_f(p) = min c_f(u, v) po łukach p.
4. Linie 6–12: dla łuku (u, v) ∈ p, który należy do sieci, f(u, v) += c_f(p);
   w przeciwnym razie (łuk przeciwny w G_f) f(v, u) −= c_f(p) — kasowanie
   przepływu.

Funkcja zwraca f oraz listę iteracji (`AugmentingPath`: ścieżka, c_f(p), łuki
z cofniętym przepływem), którą wypisuje `--steps`. `flow_value(graph, flow, s)`
to |f| = suma f na łukach wychodzących z s minus wchodzących do s (w naszych
sieciach do s nic nie wchodzi).

Dlaczego wynik jest maksymalny: gdy w G_f nie ma ścieżki s → t, zbiór S
wierzchołków osiągalnych z s w G_f wyznacza przekrój (S, V \ S), którego łuki
wychodzące są nasycone, a wchodzące mają przepływ 0 — więc |f| równa się
przepustowości tego przekroju (twierdzenie o maksymalnym przepływie i minimalnym
przekroju).

Przepustowości są całkowite, więc każda iteracja zwiększa |f| o co najmniej 1,
a przepływ wynikowy jest całkowity. Przy ścieżkach najkrótszych (BFS) odległości
w G_f nie maleją, a liczba iteracji to O(n·m) niezależnie od przepustowości.
Iteracja kosztuje O(n + m) (budowa G_f i BFS), łącznie O(n·m²). Pamięć O(n + m).
