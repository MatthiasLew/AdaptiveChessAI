# Finalna lista komend do uruchomienia badań

Ten dokument zawiera finalny zestaw komend potrzebnych do uruchomienia eksperymentów badawczych w projekcie AdaptiveChessAI.

Komendy należy wykonywać z głównego katalogu projektu.

---

## 1. Przejście do katalogu projektu

Przykład dla Windows PowerShell:

```powershell
cd C:\fork\AdaptiveChessAI
```

Jeśli projekt znajduje się w innym miejscu, należy przejść do właściwego katalogu.

---

## 2. Sprawdzenie stanu Gita

```powershell
git status
```

Oczekiwany stan:

```text
nothing to commit, working tree clean
```

Jeśli są niezacommitowane zmiany, należy je najpierw przejrzeć.

---

## 3. Sprawdzenie aktualnego commita

```powershell
git rev-parse HEAD
```

Wynik tej komendy warto zapisać w pracy albo w notatkach do eksperymentu.

Przykład zapisu:

```text
Commit eksperymentu: do uzupełnienia
```

---

## 4. Sprawdzenie wersji Pythona

```powershell
python --version
```

W projekcie należy używać wersji zgodnej z `pyproject.toml`.

---

## 5. Instalacja zależności

```powershell
pip install -r requirements.txt
```

Jeśli używasz środowiska wirtualnego, aktywuj je przed instalacją zależności.

---

## 6. Uruchomienie testów jednostkowych

```powershell
python -m pytest
```

Finalnych eksperymentów nie należy uruchamiać, jeśli testy nie przechodzą.

---

## 7. Sprawdzenie gotowości projektu

Podstawowe sprawdzenie plików i katalogów:

```powershell
python scripts/check_experiment_readiness.py
```

Pełniejsze sprawdzenie z testami:

```powershell
python scripts/check_experiment_readiness.py --run-tests
```

Najlepszy wariant przed badaniami:

```powershell
python scripts/check_experiment_readiness.py --run-tests --run-smoke-suite --smoke-with-charts
```

---

## 8. Sprawdzenie wyników smoke testu

Po smoke teście sprawdź, czy powstał katalog:

```powershell
Test-Path .\results\readiness_smoke
```

Sprawdź zbiorcze podsumowanie:

```powershell
Test-Path .\results\readiness_smoke\suite_summary.md
Get-Content .\results\readiness_smoke\suite_summary.md
```

Jeśli `suite_summary.md` nie istnieje, nie uruchamiaj finalnych badań przed naprawą pipeline’u.

---

## 9. Finalny eksperyment podstawowy

To jest główny zestaw wyników do pracy:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Parametry:

| Parametr | Wartość |
|---|---:|
| katalog wyników | `results/full_suite_v1` |
| liczba partii na konfigurację | 10 |
| limit półruchów | 80 |
| głębokość minimaxa | 1 |
| próg adjudykacji materiałowej | 3 |

---

## 10. Sprawdzenie wyników podstawowych

Po uruchomieniu sprawdź:

```powershell
Test-Path .\results\full_suite_v1
Test-Path .\results\full_suite_v1\suite_summary.md
```

Podejrzyj zbiorcze podsumowanie:

```powershell
Get-Content .\results\full_suite_v1\suite_summary.md
```

Sprawdź najważniejsze CSV:

```powershell
Test-Path .\results\full_suite_v1\random_series.csv
Test-Path .\results\full_suite_v1\random_vs_minimax.csv
Test-Path .\results\full_suite_v1\random_vs_adaptive.csv
Test-Path .\results\full_suite_v1\static_vs_adaptive.csv
```

Sprawdź metadane:

```powershell
Test-Path .\results\full_suite_v1\random_series.metadata.json
Test-Path .\results\full_suite_v1\random_vs_minimax.metadata.json
Test-Path .\results\full_suite_v1\random_vs_adaptive.metadata.json
Test-Path .\results\full_suite_v1\static_vs_adaptive.metadata.json
```

---

## 11. Sprawdzenie profili adaptacyjnych

Eksperymenty adaptacyjne powinny zawierać profile przeciwnika w metadanych.

Sprawdź:

```powershell
Get-Content .\results\full_suite_v1\random_vs_adaptive.metadata.json
Get-Content .\results\full_suite_v1\static_vs_adaptive.metadata.json
```

Szukaj pola:

```text
adaptive_profile_snapshots
```

---

## 12. Sprawdzenie raportów tekstowych

```powershell
Test-Path .\results\full_suite_v1\random_series_report.txt
Test-Path .\results\full_suite_v1\random_vs_minimax_report.txt
Test-Path .\results\full_suite_v1\random_vs_adaptive_report.txt
Test-Path .\results\full_suite_v1\static_vs_adaptive_report.txt
```

Podejrzyj raport najważniejszego porównania:

```powershell
Get-Content .\results\full_suite_v1\static_vs_adaptive_report.txt
```

---

## 13. Sprawdzenie wykresów

Sprawdź, czy istnieje katalog z wykresami:

```powershell
Test-Path .\results\full_suite_v1\charts
```

Wylistuj wygenerowane pliki:

```powershell
Get-ChildItem .\results\full_suite_v1\charts -Recurse
```

Wykresy należy otworzyć ręcznie i sprawdzić, czy nie są puste.

---

## 14. Eksperyment dodatkowy dla głębokości 2

Ten wariant jest opcjonalny.

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_depth2 --matches 3 --max-half-moves 60 --depths 2
```

Parametry:

| Parametr | Wartość |
|---|---:|
| katalog wyników | `results/full_suite_depth2` |
| liczba partii na konfigurację | 3 |
| limit półruchów | 60 |
| głębokość minimaxa | 2 |
| próg adjudykacji materiałowej | 3 |

Ten eksperyment może działać wyraźnie dłużej niż `depth=1`.

---

## 15. Sprawdzenie wyników dla głębokości 2

```powershell
Test-Path .\results\full_suite_depth2
Test-Path .\results\full_suite_depth2\suite_summary.md
Get-Content .\results\full_suite_depth2\suite_summary.md
```

---

## 16. Ręczne wygenerowanie zbiorczego podsumowania

Jeśli z jakiegoś powodu trzeba ponownie wygenerować `suite_summary.md`, użyj:

```powershell
python scripts/summarize_experiment_suite.py --input-dir results/full_suite_v1
```

Dla głębokości 2:

```powershell
python scripts/summarize_experiment_suite.py --input-dir results/full_suite_depth2
```

---

## 17. Ręczne wygenerowanie raportu z pojedynczego CSV

Przykład:

```powershell
python scripts/analyze_results_csv.py --input-csv results/full_suite_v1/static_vs_adaptive.csv --output-report results/full_suite_v1/static_vs_adaptive_report.txt
```

---

## 18. Ręczne wygenerowanie wykresów z pojedynczego CSV

Przykład:

```powershell
python scripts/generate_charts.py --input-csv results/full_suite_v1/static_vs_adaptive.csv --output-dir results/full_suite_v1/charts/static_vs_adaptive
```

---

## 19. Minimalny zestaw plików do opisania w pracy

Dla wariantu podstawowego najważniejsze pliki to:

```text
results/full_suite_v1/suite_summary.md
results/full_suite_v1/random_series_report.txt
results/full_suite_v1/random_vs_minimax_report.txt
results/full_suite_v1/random_vs_adaptive_report.txt
results/full_suite_v1/static_vs_adaptive_report.txt
results/full_suite_v1/random_vs_adaptive.metadata.json
results/full_suite_v1/static_vs_adaptive.metadata.json
results/full_suite_v1/charts/
```

---

## 20. Dane do zapisania przy eksperymencie

Po finalnym uruchomieniu zapisz:

```powershell
git rev-parse HEAD
python --version
```

Uzupełnij tabelę:

| Informacja | Wartość |
|---|---|
| data uruchomienia | do uzupełnienia |
| commit Git | do uzupełnienia |
| wersja Pythona | do uzupełnienia |
| katalog wyników | `results/full_suite_v1` |
| liczba partii | `10` |
| limit półruchów | `80` |
| głębokość minimaxa | `1` |
| próg adjudykacji | `3` |

---

## 21. Kolejność komend w skrócie

Minimalna bezpieczna sekwencja:

```powershell
git status
git rev-parse HEAD
python --version
pip install -r requirements.txt
python -m pytest
python scripts/check_experiment_readiness.py --run-tests --run-smoke-suite --smoke-with-charts
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
Get-Content .\results\full_suite_v1\suite_summary.md
```

Opcjonalnie:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_depth2 --matches 3 --max-half-moves 60 --depths 2
Get-Content .\results\full_suite_depth2\suite_summary.md
```

---

## 22. Kryterium zakończenia

Etap generowania danych można uznać za zakończony, jeśli:

- testy przechodzą,
- readiness check przechodzi,
- smoke suite przechodzi,
- finalny suite tworzy CSV,
- finalny suite tworzy metadane JSON,
- finalny suite tworzy raporty tekstowe,
- finalny suite tworzy `suite_summary.md`,
- finalny suite tworzy wykresy,
- metadane adaptacyjne zawierają `adaptive_profile_snapshots`.