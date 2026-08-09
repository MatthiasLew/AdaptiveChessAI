# Domknięcie MVP projektu AdaptiveChessAI

Ten dokument opisuje finalną decyzję dotyczącą statusu MVP projektu AdaptiveChessAI.

MVP oznacza minimalną wersję projektu wystarczającą do przeprowadzenia eksperymentów badawczych, zebrania wyników i opisania ich w pracy inżynierskiej.

---

## Decyzja

Projekt AdaptiveChessAI można uznać za domknięty na poziomie MVP badawczego.

Oznacza to, że projekt posiada kompletny minimalny pipeline potrzebny do:

- rozgrywania partii między botami,
- porównywania botów statycznych i adaptacyjnych,
- zapisywania wyników,
- generowania raportów,
- generowania wykresów,
- zapisywania metadanych eksperymentów,
- uruchamiania pełnego zestawu eksperymentów jedną komendą,
- przygotowania danych do rozdziału badawczego pracy inżynierskiej.

Projekt nie jest jeszcze pełną aplikacją użytkową z GUI, bazą danych i zaawansowanym silnikiem szachowym. Jest natomiast wystarczającą platformą badawczą do analizy działania botów adaptacyjnych.

---

## Zakres domkniętego MVP

### 1. Warstwa gry

Projekt obsługuje:

- tworzenie partii szachowej,
- wykonywanie legalnych ruchów,
- sprawdzanie stanu partii,
- wykrywanie zakończenia gry,
- pobieranie wyniku partii,
- zapisywanie końcowego FEN.

Warstwa gry bazuje na bibliotece `python-chess`.

---

### 2. Boty

W MVP dostępne są trzy główne boty:

| Bot | Status | Opis |
|---|---|---|
| `RandomBot` | gotowy | wybiera losowy legalny ruch |
| `StaticMinimaxBot` | gotowy | używa minimaxa z alfa-beta pruning |
| `AdaptiveMinimaxBot` | gotowy | używa minimaxa oraz profilu przeciwnika |

Z punktu widzenia MVP są to wystarczające typy botów do przeprowadzenia porównań badawczych.

---

### 3. Funkcja oceny pozycji

Funkcja oceny pozycji uwzględnia:

- materiał,
- mobilność,
- kontrolę centrum,
- mata,
- podstawowe sytuacje remisowe.

Funkcja oceny jest świadomie uproszczona, ale wystarczająca do porównania botów w ramach jednej platformy eksperymentalnej.

---

### 4. Algorytm wyszukiwania

Projekt zawiera:

- minimax,
- alfa-beta pruning,
- wybór najlepszego ruchu,
- testy sprawdzające podstawową poprawność wyszukiwania.

To wystarcza do budowy klasycznego bota statycznego i bota adaptacyjnego korzystającego z tego samego mechanizmu bazowego.

---

### 5. Adaptacja

Bot adaptacyjny obsługuje:

- obserwowanie ruchów przeciwnika,
- budowanie profilu przeciwnika,
- trwały profil przeciwnika między partiami w serii,
- korektę oceny ruchu na podstawie profilu,
- eksport końcowego profilu do metadanych eksperymentu.

Profil przeciwnika zapisuje:

- liczbę zaobserwowanych ruchów,
- liczbę bić,
- liczbę szachów,
- liczbę ruchów do centrum,
- współczynnik bić,
- współczynnik szachów,
- współczynnik ruchów do centrum.

---

### 6. Eksperymenty

MVP zawiera eksperymenty:

- `RandomBot vs RandomBot`,
- `RandomBot vs StaticMinimaxBot`,
- `RandomBot vs AdaptiveMinimaxBot`,
- `StaticMinimaxBot vs AdaptiveMinimaxBot`.

Najważniejszy eksperyment badawczy to:

```text
StaticMinimaxBot vs AdaptiveMinimaxBot
```

ponieważ oba boty korzystają z podobnego mechanizmu bazowego, ale tylko bot adaptacyjny wykorzystuje profil przeciwnika.

---

### 7. Wyniki i dane

Projekt zapisuje:

- CSV z wynikami partii,
- JSON z metadanymi eksperymentów,
- raporty tekstowe,
- wykresy PNG,
- zbiorcze podsumowanie Markdown.

CSV zawiera między innymi:

- nazwę eksperymentu,
- numer partii,
- nazwy botów,
- wynik formalny,
- wynik techniczny,
- powód zakończenia,
- liczbę półruchów,
- końcową przewagę materialną,
- historię ruchów,
- historię materiału,
- historię ocen pozycji,
- końcowy FEN.

---

### 8. Pipeline badawczy

Projekt posiada pełny pipeline uruchamiany jedną komendą:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Pipeline generuje:

- CSV,
- metadane JSON,
- raporty tekstowe,
- wykresy,
- `suite_summary.md`.

---

### 9. Readiness check

Projekt posiada skrypt sprawdzający gotowość eksperymentów:

```powershell
python scripts/check_experiment_readiness.py
```

Wersja pełniejsza:

```powershell
python scripts/check_experiment_readiness.py --run-tests --run-smoke-suite --smoke-with-charts
```

Ten skrypt pozwala wykryć problemy przed uruchomieniem właściwych eksperymentów.

---

### 10. Dokumentacja

Projekt posiada dokumentację dotyczącą:

- uruchamiania eksperymentów,
- statusu MVP,
- checklisty finalnego uruchomienia,
- szablonu opisu wyników,
- finalnej listy komend badawczych.

Najważniejsze dokumenty:

```text
docs/experiments.md
docs/mvp_status.md
docs/final_experiment_checklist.md
docs/results_writeup_template.md
docs/final_research_commands.md
docs/mvp_closure.md
```

---

## Kryteria akceptacji MVP

MVP można uznać za domknięte, jeśli spełnione są następujące warunki:

| Kryterium | Status |
|---|---|
| działa `RandomBot` | spełnione |
| działa `StaticMinimaxBot` | spełnione |
| działa `AdaptiveMinimaxBot` | spełnione |
| działa rozgrywanie partii | spełnione |
| działa rozgrywanie serii | spełnione |
| działa minimax | spełnione |
| działa alfa-beta pruning | spełnione |
| działa profil przeciwnika | spełnione |
| profil przeciwnika może być trwały w serii | spełnione |
| profil przeciwnika trafia do metadanych | spełnione |
| działa eksport CSV | spełnione |
| działa eksport metadanych JSON | spełnione |
| działa analiza CSV | spełnione |
| działają raporty tekstowe | spełnione |
| działają wykresy | spełnione |
| działa pełny suite eksperymentów | spełnione |
| działa readiness check | spełnione |
| istnieje dokumentacja eksperymentów | spełnione |

Na podstawie tych kryteriów projekt spełnia wymagania MVP badawczego.

---

## Elementy świadomie poza MVP

Poniższe elementy nie są wymagane do domknięcia MVP.

### GUI

Projekt nie posiada jeszcze graficznego interfejsu użytkownika.

GUI może być dodane później, ale nie jest konieczne do przeprowadzenia eksperymentów badawczych.

---

### Baza danych

Projekt zapisuje wyniki do CSV i JSON.

Baza danych, np. SQLite, może być przydatna w przyszłości, ale nie jest wymagana do obecnej wersji badawczej.

---

### Silniejszy silnik szachowy

Projekt nie ma na celu konkurowania z profesjonalnymi silnikami szachowymi.

Niska głębokość minimaxa jest akceptowalna, ponieważ celem jest porównanie zachowania botów w kontrolowanych warunkach, a nie osiągnięcie profesjonalnej siły gry.

---

### Zaawansowane uczenie maszynowe

Obecna adaptacja jest heurystyczna.

Projekt nie wymaga pełnego modelu ML, aby spełnić cel badawczy. Heurystyczny profil przeciwnika jest wystarczający do porównania bota statycznego i adaptacyjnego.

---

### Zaawansowana funkcja oceny

Funkcja oceny pozycji może być rozwijana, ale obecna wersja jest wystarczająca dla MVP.

Potencjalne rozszerzenia:

- bezpieczeństwo króla,
- struktura pionów,
- rozwój figur,
- tablice pól figur,
- kontrola linii,
- ocena tempa.

---

## Minimalny finalny zestaw eksperymentów

Rekomendowany minimalny eksperyment do pracy:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Ten zestaw generuje dane wystarczające do opisania:

- baseline’u losowego,
- przewagi minimaxa nad botem losowym,
- działania bota adaptacyjnego względem bota losowego,
- porównania bota adaptacyjnego z botem statycznym.

---

## Opcjonalny zestaw rozszerzony

Opcjonalnie można uruchomić:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_depth2 --matches 3 --max-half-moves 60 --depths 2
```

Ten zestaw może być użyty jako dodatkowe porównanie wpływu większej głębokości minimaxa.

Nie jest wymagany do minimalnego MVP.

---

## Zalecana kolejność dalszych działań

Po domknięciu MVP zalecana kolejność prac jest następująca:

1. Uruchomić pełny readiness check.
2. Uruchomić smoke suite.
3. Uruchomić finalny suite `full_suite_v1`.
4. Sprawdzić `suite_summary.md`.
5. Sprawdzić raporty tekstowe.
6. Sprawdzić wykresy.
7. Sprawdzić metadane adaptacyjne.
8. Uzupełnić `docs/results_writeup_template.md` konkretnymi wynikami.
9. Przenieść opis implementacji i wyników do pracy inżynierskiej.
10. Dopiero potem decydować, czy warto dodawać GUI, SQLite albo silniejszą funkcję oceny.

---

## Decyzja projektowa

Na tym etapie nie należy już dodawać dużych funkcji do MVP przed pierwszym uruchomieniem finalnych badań.

Najpierw należy wygenerować dane i zobaczyć wyniki.

Dalsze funkcje powinny być dodawane tylko wtedy, gdy:

- wyniki pokażą istotny problem,
- brakuje danych do opisu pracy,
- promotor wymaga konkretnego rozszerzenia,
- czas pozwala na rozszerzenie bez ryzyka destabilizacji projektu.

---

## Finalny status

Status projektu:

```text
MVP badawcze: domknięte
```

Następny właściwy krok:

```text
uruchomienie finalnych eksperymentów i analiza wyników
```

Najważniejsza komenda:

```powershell
python scripts/check_experiment_readiness.py --run-tests --run-smoke-suite --smoke-with-charts
```

Po niej:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```