# Eksperymenty

Ten dokument opisuje sposób uruchamiania eksperymentów w projekcie AdaptiveChessAI.

Eksperymenty służą do porównywania skuteczności różnych botów szachowych:

- `RandomBot`
- `StaticMinimaxBot`
- `AdaptiveMinimaxBot`

Wyniki mogą być zapisywane do plików CSV, analizowane jako raporty tekstowe oraz wizualizowane na wykresach PNG.

---

## Wymagania

Przed uruchomieniem eksperymentów należy zainstalować zależności:

```powershell
pip install -r requirements.txt
```

Podstawowe sprawdzenie projektu:

```powershell
python -m pytest
```

---

## Główne typy wyników

Każda partia ma dwa rodzaje wyniku:

| Pole | Znaczenie |
|---|---|
| `result` | wynik formalny partii |
| `adjudicated_result` | wynik techniczny po adjudykacji materiałowej |

Wynik formalny pochodzi bezpośrednio z zasad gry albo z technicznego remisu po osiągnięciu limitu półruchów.

Wynik techniczny jest używany dla partii przerwanych limitem. Jeśli jedna ze stron ma odpowiednio dużą przewagę materialną, wynik techniczny może zostać przypisany tej stronie.

Domyślny próg adjudykacji:

```text
3 punkty materiału
```

Czyli przewaga co najmniej lekkiej figury.

---

## RandomBot vs RandomBot

Eksperyment bazowy:

```powershell
python scripts/run_random_series.py --matches 20 --max-half-moves 100 --output-csv results/random_series.csv
```

Wyniki:

```text
results/random_series.csv
results/random_series.metadata.json
```

Ten eksperyment sprawdza działanie mechanizmu serii partii i statystyk.

---

## RandomBot vs StaticMinimaxBot

Eksperyment porównujący bota losowego z klasycznym botem minimaxowym:

```powershell
python scripts/run_random_vs_minimax_series.py --matches 10 --max-half-moves 80 --depths 1 --output-csv results/random_vs_minimax.csv
```

Można testować kilka głębokości:

```powershell
python scripts/run_random_vs_minimax_series.py --matches 5 --max-half-moves 80 --depths 1 2 --output-csv results/random_vs_minimax.csv
```

Wyniki:

```text
results/random_vs_minimax.csv
results/random_vs_minimax.metadata.json
```

---

## RandomBot vs AdaptiveMinimaxBot

Eksperyment porównujący bota losowego z botem adaptacyjnym:

```powershell
python scripts/run_random_vs_adaptive_series.py --matches 10 --max-half-moves 80 --depths 1 --output-csv results/random_vs_adaptive.csv
```

Wyniki:

```text
results/random_vs_adaptive.csv
results/random_vs_adaptive.metadata.json
```

Metadane zawierają także końcowe profile przeciwnika zebrane przez bota adaptacyjnego.

---

## StaticMinimaxBot vs AdaptiveMinimaxBot

Eksperyment porównujący klasycznego minimaxa z botem adaptacyjnym:

```powershell
python scripts/run_static_vs_adaptive_series.py --matches 10 --max-half-moves 80 --depths 1 --output-csv results/static_vs_adaptive.csv
```

Wyniki:

```text
results/static_vs_adaptive.csv
results/static_vs_adaptive.metadata.json
```

Ten eksperyment jest szczególnie ważny, ponieważ oba boty używają podobnego mechanizmu bazowego, ale `AdaptiveMinimaxBot` dodatkowo korzysta z profilu przeciwnika.

---

## Pełny zestaw eksperymentów

Pełny pipeline eksperymentalny można uruchomić jedną komendą:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Skrypt uruchamia:

- `RandomBot vs RandomBot`
- `RandomBot vs StaticMinimaxBot`
- `RandomBot vs AdaptiveMinimaxBot`
- `StaticMinimaxBot vs AdaptiveMinimaxBot`

Dodatkowo generuje:

- pliki CSV,
- pliki metadanych JSON,
- raporty tekstowe,
- wykresy PNG.

Przykładowa struktura wyników:

```text
results/full_suite_v1/
├── random_series.csv
├── random_series.metadata.json
├── random_series_report.txt
├── random_vs_minimax.csv
├── random_vs_minimax.metadata.json
├── random_vs_minimax_report.txt
├── random_vs_adaptive.csv
├── random_vs_adaptive.metadata.json
├── random_vs_adaptive_report.txt
├── static_vs_adaptive.csv
├── static_vs_adaptive.metadata.json
├── static_vs_adaptive_report.txt
└── charts/
```

---

## Raport tekstowy z CSV

Jeśli istnieje plik CSV z wynikami, można wygenerować raport:

```powershell
python scripts/analyze_results_csv.py --input-csv results/random_vs_minimax.csv --output-report results/random_vs_minimax_report.txt
```

Raport zawiera:

- liczbę partii,
- wyniki formalne,
- wyniki techniczne,
- średnią liczbę półruchów,
- średnią końcową przewagę materialną,
- liczbę partii zakończonych limitem.

---

## Wykresy z CSV

Wykresy można wygenerować komendą:

```powershell
python scripts/generate_charts.py --input-csv results/random_vs_minimax.csv --output-dir results/charts/random_vs_minimax
```

Generowane są wykresy:

```text
adjudicated_results.png
average_final_material_balance.png
move_limit_counts.png
```

---

## Zalecane ustawienia testowe

Szybkie testy techniczne:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_test --matches 2 --max-half-moves 20 --depths 1
```

Rozsądne ustawienie do pierwszych wyników badawczych:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Ostrożny test głębokości `2`:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_depth2_test --matches 3 --max-half-moves 60 --depths 2
```

Głębszy minimax może działać wolno, dlatego większe serie należy uruchamiać dopiero po sprawdzeniu czasu działania na małej liczbie partii.

---

## Metadane eksperymentów

Dla każdego CSV generowany jest plik:

```text
*.metadata.json
```

Metadane zawierają między innymi:

- typ eksperymentu,
- liczbę partii,
- limit półruchów,
- testowane głębokości,
- próg adjudykacji materiałowej,
- wersję funkcji oceny pozycji,
- wersję bota adaptacyjnego,
- konfigurację serii,
- końcowe profile przeciwnika dla eksperymentów adaptacyjnych.

Metadane są ważne dla powtarzalności badań, ponieważ pozwalają powiązać wyniki z konkretną konfiguracją uruchomienia.