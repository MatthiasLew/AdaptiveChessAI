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

## Finalne uruchomienie eksperymentów

Checklista finalnego uruchomienia eksperymentów znajduje się w:

```text
docs/final_experiment_checklist.md
```

Szablon opisu wyników do pracy inżynierskiej znajduje się w:

```text
docs/results_writeup_template.md
```

## Finalne komendy badawcze

Finalna lista komend do uruchomienia badań znajduje się w:

```text
docs/final_research_commands.md
```

## Domknięcie MVP

Status domknięcia MVP opisano w dokumencie:

```text
docs/mvp_closure.md
```

Aktualna decyzja projektowa:

```text
MVP badawcze: domknięte
```

Następny krok po domknięciu MVP:

```text
uruchomienie finalnych eksperymentów i analiza wyników
```