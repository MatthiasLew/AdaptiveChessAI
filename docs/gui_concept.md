# Koncepcja GUI aplikacji AdaptiveChessAI

Ten dokument opisuje zatwierdzoną koncepcję graficznego interfejsu aplikacji AdaptiveChessAI.

Projekt nie ma być prostym jednoekranowym GUI. Aplikacja ma mieć czytelną strukturę wieloekranową, ponieważ łączy dwa główne tryby:

- grę człowieka z botem,
- eksperymenty i analizę wyników.

---

## Decyzja projektowa

Zatwierdzony wariant GUI:

```text
aplikacja desktopowa z menu głównym i osobnymi ekranami roboczymi
```

Główne ekrany:

1. Ekran startowy / menu główne.
2. Ekran gry z botem.
3. Ekran po zakończonej partii.
4. Ekran konfiguracji eksperymentów.
5. Ekran logu działania eksperymentów.
6. Ekran wyników i raportów.
7. Ekran ustawień, opcjonalnie w późniejszym etapie.

---

## Styl aplikacji

Preferowany styl:

- ciemny motyw,
- czytelne kontrasty,
- duże przyciski na ekranie startowym,
- wyraźny podział między grą i częścią badawczą,
- układ przypominający aplikację desktopową, nie tylko prostą planszę szachową,
- minimum zbędnych elementów,
- nacisk na czytelność.

---

## Ekran 1 — menu główne

Menu główne jest pierwszym ekranem po uruchomieniu aplikacji.

### Cel

Użytkownik powinien od razu widzieć, co może zrobić.

### Elementy

- logo lub nazwa aplikacji,
- krótki opis projektu,
- przycisk `Graj z botem`,
- przycisk `Eksperymenty`,
- przycisk `Wyniki`,
- przycisk `Ustawienia`,
- przycisk `Wyjście`.

### Szkic

```text
+------------------------------------------------+
| AdaptiveChessAI                                |
| Inteligentne szachy. Adaptacyjna nauka.        |
|                                                |
| [ Graj z botem ]                               |
| [ Eksperymenty ]                               |
| [ Wyniki ]                                     |
| [ Ustawienia ]                                 |
| [ Wyjście ]                                    |
+------------------------------------------------+
```

---

## Ekran 2 — gra z botem

To główny ekran aplikacyjny.

### Cel

Użytkownik może rozegrać partię przeciwko wybranemu botowi.

### Elementy

- szachownica,
- panel ustawień gry,
- wybór bota,
- wybór koloru gracza,
- wybór głębokości minimaxa,
- przycisk `Nowa gra`,
- przycisk `Zapisz partię`,
- status gry,
- historia ruchów,
- przycisk powrotu do menu.

### Boty dostępne w GUI

- `RandomBot`,
- `StaticMinimaxBot`,
- `AdaptiveMinimaxBot`.

### Szkic

```text
+--------------------------------------------------------------+
| AdaptiveChessAI — Gra z botem                                |
+--------------------------------------+-----------------------+
|                                      | Ustawienia gry        |
|                                      | Bot: [RandomBot ▼]    |
|             SZACHOWNICA              | Kolor: [Białe ▼]      |
|                                      | Depth: [1]            |
|                                      |                       |
|                                      | [Nowa gra]            |
|                                      | [Zapisz partię]       |
|                                      | [Powrót do menu]      |
+--------------------------------------+-----------------------+
| Historia ruchów                      | Status: Tura białych |
+--------------------------------------------------------------+
```

---

## Ekran 3 — podsumowanie partii

Ten ekran pojawia się po zakończeniu partii albo po ręcznym zapisaniu wyniku.

### Cel

Pokazać użytkownikowi wynik i podstawowe statystyki partii.

### Elementy

- wynik partii,
- zwycięzca albo remis,
- liczba ruchów,
- końcowa przewaga materiałowa,
- historia ruchów,
- prosty wykres przewagi materiałowej, opcjonalnie,
- przycisk `Nowa gra`,
- przycisk `Zapisz partię`,
- przycisk `Powrót do menu`.

### Szkic

```text
+--------------------------------------------------------------+
| AdaptiveChessAI — Wynik partii                               |
+------------------------------+-------------------------------+
| Wynik partii                 | Historia ruchów               |
| 1 - 0                        | 1. e4 e5                      |
| Zwycięstwo białych           | 2. Nf3 Nc6                    |
|                              | ...                           |
| Liczba ruchów: 42            |                               |
| Przewaga materiału: +3.2     |                               |
|                              |                               |
| [Nowa gra] [Zapisz] [Menu]   |                               |
+------------------------------+-------------------------------+
```

---

## Ekran 4 — konfiguracja eksperymentów

Ten ekran służy do uruchamiania eksperymentów bot vs bot.

### Cel

Użytkownik może skonfigurować eksperyment bez wpisywania komend w terminalu.

### Elementy

- lista dostępnych eksperymentów,
- liczba partii,
- limit półruchów,
- głębokość minimaxa,
- folder wyników,
- opcje dodatkowe,
- przycisk `Uruchom eksperyment`,
- przycisk `Anuluj`,
- przycisk `Powrót do menu`.

### Dostępne eksperymenty

- `Full suite`,
- `RandomBot vs RandomBot`,
- `RandomBot vs StaticMinimaxBot`,
- `RandomBot vs AdaptiveMinimaxBot`,
- `StaticMinimaxBot vs AdaptiveMinimaxBot`.

### Szkic

```text
+--------------------------------------------------------------+
| AdaptiveChessAI — Eksperymenty                               |
+-----------------------------+--------------------------------+
| Dostępne eksperymenty       | Ustawienia eksperymentu       |
| > Full suite                | Partie: [10]                  |
| > Random vs Random          | Limit półruchów: [80]         |
| > Random vs Minimax         | Depth: [1]                    |
| > Random vs Adaptive        | Folder: results/full_suite_v1 |
| > Static vs Adaptive        |                                |
|                             | [Uruchom eksperyment]         |
|                             | [Powrót do menu]              |
+-----------------------------+--------------------------------+
```

---

## Ekran 5 — log działania eksperymentu

Ten ekran pokazuje przebieg eksperymentu.

### Cel

Użytkownik widzi, czy eksperyment działa, ile wykonano partii i gdzie zapisano wyniki.

### Elementy

- log tekstowy,
- pasek postępu,
- aktualny status,
- przycisk `Otwórz folder wyników`,
- przycisk `Zamknij`,
- przycisk `Powrót do menu`.

### Szkic

```text
+--------------------------------------------------------------+
| AdaptiveChessAI — Eksperyment w toku                         |
+--------------------------------------------------------------+
| [12:15:03] Start eksperymentu Full suite                      |
| [12:15:04] RandomBot vs RandomBot                             |
| [12:15:10] Partia 1/10 zakończona                             |
| [12:15:16] Partia 2/10 zakończona                             |
| ...                                                          |
|                                                              |
| Postęp: [############------] 66%                              |
|                                                              |
| [Otwórz folder wyników] [Zamknij] [Powrót do menu]            |
+--------------------------------------------------------------+
```

---

## Ekran 6 — wyniki i raporty

Ten ekran służy do przeglądania wyników eksperymentów.

### Cel

Użytkownik może wczytać folder wyników i zobaczyć podsumowanie bez ręcznego otwierania plików.

### Elementy

- wybór folderu wyników,
- przycisk `Wczytaj`,
- tabela podsumowania,
- zakładki lub sekcje:
  - podsumowanie,
  - szczegóły,
  - wykresy,
  - partie,
- przyciski:
  - `Otwórz raport`,
  - `Otwórz folder wykresów`,
  - `Eksportuj CSV`,
  - `Powrót do menu`.

### Szkic

```text
+--------------------------------------------------------------+
| AdaptiveChessAI — Wyniki                                     |
+--------------------------------------------------------------+
| Folder wyników: [results/full_suite_v1] [Wczytaj]            |
+--------------------------------------------------------------+
| Podsumowanie | Szczegóły | Wykresy | Partie                  |
+--------------------------------------------------------------+
| Eksperyment              | Partie | Wyniki | Śr. materiał     |
| Random vs Random         | 10     | ...    | ...              |
| Random vs Minimax        | 10     | ...    | ...              |
| Random vs Adaptive       | 10     | ...    | ...              |
| Static vs Adaptive       | 10     | ...    | ...              |
+--------------------------------------------------------------+
| [Otwórz raport] [Otwórz wykresy] [Powrót do menu]            |
+--------------------------------------------------------------+
```

---

## Ekran 7 — ustawienia

Ekran ustawień jest opcjonalny dla pierwszej wersji GUI.

### Możliwe ustawienia

- domyślny bot,
- domyślny kolor gracza,
- domyślna głębokość minimaxa,
- domyślny folder wyników,
- motyw jasny/ciemny,
- rozmiar planszy.

W pierwszej wersji GUI ekran ustawień może istnieć jako prosty placeholder albo może zostać odłożony.

---

## Nawigacja

Aplikacja ma mieć prostą nawigację:

```text
Menu główne
 ├── Gra z botem
 │    └── Podsumowanie partii
 ├── Eksperymenty
 │    └── Log eksperymentu
 ├── Wyniki
 ├── Ustawienia
 └── Wyjście
```

Każdy główny ekran powinien mieć przycisk:

```text
Powrót do menu
```

---

## Technologia GUI

Rekomendowana technologia:

```text
PySide6
```

Uzasadnienie:

- dobra obsługa aplikacji desktopowych,
- naturalne okna, przyciski, formularze i tabele,
- nadaje się do aplikacji inżynierskiej,
- pozwala tworzyć własny widget szachownicy,
- dobrze działa na Windowsie.

---

## Sposób renderowania szachownicy

Pierwsza wersja:

```text
własny widget szachownicy + figury Unicode
```

Przykładowe figury:

```text
♙ ♘ ♗ ♖ ♕ ♔
♟ ♞ ♝ ♜ ♛ ♚
```

Grafiki figur SVG/PNG można dodać później.

---

## Sposób wykonywania ruchów

Pierwsza wersja:

```text
kliknięcie pola źródłowego
kliknięcie pola docelowego
```

Nie dodajemy na start drag and drop.

Drag and drop można dodać później.

---

## Zakres pierwszego GUI MVP

Pierwsze aplikacyjne MVP powinno zawierać:

- menu główne,
- ekran gry z botem,
- szachownicę,
- wybór bota,
- wybór koloru,
- wybór głębokości,
- wykonywanie ruchów przez kliknięcia,
- automatyczną odpowiedź bota,
- status gry,
- historię ruchów,
- reset gry,
- powrót do menu.

Eksperymenty i wyniki mogą być w pierwszej wersji uproszczone.

---

## Zakres poza pierwszym GUI MVP

Na start nie robimy:

- drag and drop,
- animacji ruchów,
- pełnego edytora pozycji,
- kont użytkowników,
- zapisu do bazy danych,
- silnika Stockfish,
- zaawansowanej analizy silnikowej,
- pełnego dashboardu wykresów wbudowanego w aplikację,
- trybu multiplayer.

---

## Priorytet implementacji

Kolejność prac:

1. Dodać zależność `PySide6`.
2. Stworzyć główne okno aplikacji.
3. Stworzyć ekran menu.
4. Dodać przełączanie ekranów.
5. Dodać ekran gry.
6. Dodać widget szachownicy.
7. Podpiąć `HumanVsBotSession`.
8. Dodać historię ruchów i status.
9. Dodać ekran podsumowania partii.
10. Dodać podstawowy ekran eksperymentów.
11. Dodać ekran wyników.
12. Uzupełnić dokumentację uruchamiania GUI.

---

## Kryterium gotowości GUI MVP

GUI MVP będzie gotowe, jeśli użytkownik może:

- uruchomić aplikację,
- wejść z menu w tryb gry,
- wybrać bota,
- wybrać kolor,
- wykonać ruch na szachownicy,
- dostać odpowiedź bota,
- widzieć historię ruchów,
- widzieć status gry,
- zakończyć lub zresetować partię,
- wrócić do menu.

---

## Decyzja końcowa

Zatwierdzony kierunek:

```text
AdaptiveChessAI będzie wieloekranową aplikacją desktopową z menu głównym.
Pierwszym priorytetem GUI będzie tryb gry człowiek vs bot.
Część eksperymentalna i wyniki zostaną dodane jako osobne ekrany aplikacji.
```