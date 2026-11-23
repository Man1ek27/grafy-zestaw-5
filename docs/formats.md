# Formaty wejścia i wyjścia

Pliki mają kodowanie UTF-8. Wierzchołki są numerowane od 1 do n; źródło s = 1,
ujście t = n.

## Sieć przepływowa (`--input`, `--output`) — `network`, `ford-fulkerson`

Format „lista łuków z wagami” z zestawu 4, w którym wagą jest przepustowość.
Pierwsza niepusta linia: n. Każda kolejna niepusta linia opisuje jeden łuk:
`u v c` (łuk u → v o przepustowości c). Przykład — sieć z rys. 1 w input_5.pdf
(`examples/input-5.txt`; s = 1, a..i = 2..10, t = 11):

```text
11
1 2 10
1 3 3
1 4 6
2 3 8
...
10 11 7
```

Błąd: brak n, linia bez trzech liczb, wierzchołek spoza 1..n, pętla, powtórzony
łuk, n < 2, przepustowość mniejsza niż 1, łuk wchodzący do s (1) lub wychodzący
z t (n), para łuków przeciwnych u → v i v → u.

`--output` zapisuje sieć (wylosowaną albo wczytaną) w tym samym formacie,
z łukami posortowanymi po (początek, koniec).

## Wyjście tekstowe

W wyjściu źródło jest wypisywane jako `s`, ujście jako `t`, pozostałe wierzchołki
jako numery.

- Nagłówek `Sieć: n = …, m = …, źródło s = 1, ujście t = n` i warstwy, jedna
  linia na warstwę: `numer_warstwy: wierzchołki`.
- `network` — tabela `u v c(u,v)` oraz macierz przepustowości (wiersz u,
  kolumna v, 0 = brak łuku).
- `ford-fulkerson` — liczba ścieżek powiększających, tabela `u v f/c`
  i wiersz `Wartość maksymalnego przepływu |f_max| = …`. `--steps` dodaje
  ponumerowane ścieżki powiększające w kolejności znalezienia:

  ```text
  6) s -> 4 -> 5 -> 2 -> 3 -> 7 -> 8 -> t, c_f(p) = 5, cofnięto przepływ na łuku 2 -> 5
  ```

## Rysunki PNG

- Warstwy są kolumnami od s (z lewej) do t (z prawej); wierzchołki w kolumnie są
  lekko przesunięte w pionie, jak na rys. 1 w input_5.pdf. s i t mają inny kolor.
- Łuk, który narysowany prosto przeszedłby przez inny wierzchołek, jest wygięty;
  etykiety łuków są rozsuwane, żeby się nie nakładały.
- `network` — na łukach przepustowości c(u, v).
- `ford-fulkerson` — na łukach f(u, v)/c(u, v), łuki z dodatnim przepływem są
  czerwone, w tytule |f_max|.

Katalogi wyjściowe są tworzone automatycznie; istniejące pliki są nadpisywane.
