# Finalna checklista uruchomienia eksperymentów

Ten dokument opisuje kolejność czynności przed wygenerowaniem finalnych wyników do pracy inżynierskiej.

Celem checklisty jest upewnienie się, że eksperymenty zostały uruchomione w sposób powtarzalny, kontrolowany i możliwy do późniejszego opisania.

---

## 1. Sprawdzenie repozytorium

Przed uruchomieniem eksperymentów należy sprawdzić stan repozytorium:

```powershell
git status
```

Oczekiwany stan:

```text
nothing to commit, working tree clean
```

Jeśli istnieją niezacommitowane zmiany, należy je najpierw przejrzeć i zapisać commitem albo świadomie odrzucić.

---

## 2. Instalacja zależności

Zależności projektu:

```powershell
pip install -r requirements.txt
```

Projekt korzysta przede wszystkim z:

- `python-chess`,
- `pytest`,
- `pandas`,
- `matplotlib`.

---

## 3. Uruchomienie testów jednostkowych

Przed generowaniem wyników należy uruchomić testy:

```powershell
python -m pytest
```

Wynik powinien być pozytywny.

Nie należy generować finalnych danych badawczych, jeśli testy nie przechodzą.

---

## 4. Sprawdzenie gotowości eksperymentów

Podstawowy check:

```powershell
python scripts/check_experiment_readiness.py
```

Pełniejszy check z testami:

```powershell
python scripts/check_experiment_readiness.py --run-tests
```

Smoke test całego pipeline’u:

```powershell
python scripts/check_experiment_readiness.py --run-tests --run-smoke-suite
```

Smoke test z wykresami:

```powershell
python scripts/check_experiment_readiness.py --run-tests --run-smoke-suite --smoke-with-charts
```

---

## 5. Oczekiwane pliki po smoke teście

Po smoke teście powinien istnieć katalog:

```text
results/readiness_smoke/
```

W środku powinny znajdować się między innymi:

```text
random_series.csv
random_vs_minimax.csv
random_vs_adaptive.csv
static_vs_adaptive.csv
suite_summary.md
```

Jeśli smoke test nie tworzy tych plików, należy naprawić pipeline przed uruchomieniem właściwych eksperymentów.

---

## 6. Finalne uruchomienie eksperymentów — wariant podstawowy

Zalecany pierwszy zestaw wyników do pracy:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Parametry:

| Parametr | Wartość |
|---|---:|
| liczba partii na konfigurację | 10 |
| limit półruchów | 80 |
| głębokość minimaxa | 1 |
| próg adjudykacji materiałowej | 3 |

Ten zestaw jest rozsądnym kompromisem między czasem działania a ilością danych.

---

## 7. Finalne uruchomienie eksperymentów — wariant dodatkowy

Opcjonalny zestaw porównawczy dla głębokości `2`:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_depth2 --matches 3 --max-half-moves 60 --depths 2
```

Parametry:

| Parametr | Wartość |
|---|---:|
| liczba partii na konfigurację | 3 |
| limit półruchów | 60 |
| głębokość minimaxa | 2 |
| próg adjudykacji materiałowej | 3 |

Ten wariant może działać dłużej. Nie należy zaczynać od dużej liczby partii dla głębokości `2`.

---

## 8. Pliki oczekiwane po finalnym uruchomieniu

Dla katalogu:

```text
results/full_suite_v1/
```

oczekiwane pliki:

```text
random_series.csv
random_series.metadata.json
random_series_report.txt

random_vs_minimax.csv
random_vs_minimax.metadata.json
random_vs_minimax_report.txt

random_vs_adaptive.csv
random_vs_adaptive.metadata.json
random_vs_adaptive_report.txt

static_vs_adaptive.csv
static_vs_adaptive.metadata.json
static_vs_adaptive_report.txt

suite_summary.md
charts/
```

---

## 9. Kontrola metadanych

Dla każdego eksperymentu powinien istnieć plik:

```text
*.metadata.json
```

W metadanych należy sprawdzić:

- typ eksperymentu,
- liczbę partii,
- limit półruchów,
- głębokość minimaxa,
- próg adjudykacji materiałowej,
- wersję funkcji oceny pozycji,
- wersję bota adaptacyjnego.

Dla eksperymentów adaptacyjnych należy dodatkowo sprawdzić pole:

```text
adaptive_profile_snapshots
```

Dotyczy to plików:

```text
random_vs_adaptive.metadata.json
static_vs_adaptive.metadata.json
```

---

## 10. Kontrola CSV

Każdy CSV powinien zawierać kolumny:

```text
experiment_name
match_index
white_bot_name
black_bot_name
result
adjudicated_result
termination_reason
half_moves
final_material_balance
reached_move_limit
moves_uci
material_balances
position_scores
final_fen
```

Najważniejsze pola do analizy:

| Pole | Znaczenie |
|---|---|
| `result` | wynik formalny |
| `adjudicated_result` | wynik techniczny po adjudykacji |
| `half_moves` | długość partii w półruchach |
| `final_material_balance` | końcowa przewaga materialna białych |
| `reached_move_limit` | czy partia zakończyła się limitem |
| `termination_reason` | powód zakończenia partii |

---

## 11. Kontrola raportów tekstowych

Raporty tekstowe powinny zawierać:

- liczbę partii,
- wyniki formalne,
- wyniki techniczne,
- średnią liczbę półruchów,
- średnią końcową przewagę materialną,
- liczbę partii zakończonych limitem.

Przykładowe raporty:

```text
random_vs_minimax_report.txt
random_vs_adaptive_report.txt
static_vs_adaptive_report.txt
```

---

## 12. Kontrola zbiorczego raportu

Zbiorczy raport:

```text
suite_summary.md
```

powinien zawierać tabelę porównującą wszystkie grupy eksperymentalne.

Należy sprawdzić:

- czy wszystkie eksperymenty są obecne,
- czy liczby partii są poprawne,
- czy wyniki formalne i techniczne są rozdzielone,
- czy średnie wartości są widoczne,
- czy liczba partii zakończonych limitem jest podana.

---

## 13. Kontrola wykresów

W katalogu:

```text
charts/
```

powinny znajdować się wykresy dla eksperymentów.

Typowe pliki:

```text
adjudicated_results.png
average_final_material_balance.png
move_limit_counts.png
```

Wykresy należy sprawdzić wizualnie:

- czy pliki się otwierają,
- czy wykresy nie są puste,
- czy podpisy osi są czytelne,
- czy dane odpowiadają raportom tekstowym.

---

## 14. Minimalny zestaw danych do opisania w pracy

Minimalnie w pracy należy opisać wyniki z:

```text
results/full_suite_v1/
```

Najważniejsze porównania:

1. `RandomBot vs RandomBot`
2. `RandomBot vs StaticMinimaxBot`
3. `RandomBot vs AdaptiveMinimaxBot`
4. `StaticMinimaxBot vs AdaptiveMinimaxBot`

Najważniejsze pytanie badawcze:

```text
Czy bot adaptacyjny uzyskuje inne wyniki niż bot statyczny przy podobnym mechanizmie bazowym?
```

---

## 15. Co zapisać przed opisem wyników

Przed pisaniem rozdziału z wynikami należy zanotować:

| Informacja | Wartość |
|---|---|
| data uruchomienia | do uzupełnienia |
| commit Git | do uzupełnienia |
| Python | do uzupełnienia |
| liczba partii | do uzupełnienia |
| limit półruchów | do uzupełnienia |
| głębokość minimaxa | do uzupełnienia |
| próg adjudykacji | do uzupełnienia |
| wersja oceny pozycji | do uzupełnienia |
| wersja bota adaptacyjnego | do uzupełnienia |

Commit można sprawdzić komendą:

```powershell
git rev-parse HEAD
```

Wersję Pythona:

```powershell
python --version
```

---

## 16. Kryteria uznania eksperymentów za poprawnie wykonane

Eksperymenty można uznać za poprawnie wykonane, jeśli:

- testy jednostkowe przechodzą,
- readiness check przechodzi,
- smoke test przechodzi,
- finalny suite generuje CSV,
- finalny suite generuje metadane JSON,
- finalny suite generuje raporty tekstowe,
- finalny suite generuje zbiorczy raport Markdown,
- wykresy są możliwe do otwarcia,
- metadane adaptacyjne zawierają profile przeciwnika,
- parametry eksperymentów są zapisane i możliwe do odtworzenia.

---

## 17. Najczęstsze problemy

### Testy nie przechodzą

Nie uruchamiać finalnych eksperymentów. Najpierw naprawić testy.

### Brak pliku `suite_summary.md`

Sprawdzić, czy istnieje skrypt:

```text
scripts/summarize_experiment_suite.py
```

oraz czy `run_full_experiment_suite.py` uruchamia komendę `suite_summary`.

### Brak wykresów

Sprawdzić, czy nie użyto flagi:

```text
--skip-charts
```

### Długi czas działania

Zmniejszyć:

- `--matches`,
- `--max-half-moves`,
- `--depths`.

Dla testów technicznych używać:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_test --matches 2 --max-half-moves 20 --depths 1
```

---

## 18. Wniosek

Po przejściu tej checklisty projekt jest gotowy do wygenerowania wyników, które można wykorzystać w pracy inżynierskiej.