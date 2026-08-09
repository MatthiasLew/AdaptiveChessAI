## Eksperymenty

Projekt zawiera skrypty do uruchamiania eksperymentów porównujących boty szachowe:

- `RandomBot`
- `StaticMinimaxBot`
- `AdaptiveMinimaxBot`

Podstawowy pełny zestaw eksperymentów można uruchomić komendą:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Skrypt generuje:

- pliki CSV z wynikami partii,
- pliki metadanych JSON,
- raporty tekstowe,
- wykresy PNG.

Szczegółowy opis uruchamiania eksperymentów znajduje się w:

```text
docs/experiments.md
```

Przed uruchomieniem eksperymentów należy zainstalować zależności:

```powershell
pip install -r requirements.txt
```

Testy projektu:

```powershell
python -m pytest
```

## Status MVP

Aktualny status MVP projektu opisano w dokumencie:

```text
docs/mvp_status.md
```

Dokument zawiera:

- podsumowanie obecnego zakresu projektu,
- opis działających komponentów,
- ograniczenia aktualnej wersji,
- plan domknięcia MVP,
- proponowany zestaw eksperymentów do pracy inżynierskiej.