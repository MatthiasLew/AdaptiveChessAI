# Testy AdaptiveChessAI

Testy są pogrupowane według warstwy aplikacji. Nazwy przypadków opisują zachowanie i oczekiwany wynik. Dane badawcze używane w testach są syntetyczne; każdy test zapisu korzysta z własnego katalogu tymczasowego.

| Obszar nowych funkcji | Plik | Sprawdzane zachowanie |
|---|---|---|
| Metody uczenia | `unit/learning/test_research_agents.py` | Imitacja ruchów człowieka, nagrody TD, remis, brak podwójnej aktualizacji, zamrożenie, limit węzłów, deterministyczność, mat i nieprawidłowe wagi |
| Trwałość i protokół | `unit/experiments/test_research.py` | Walidacja konfiguracji i checkpointów, zmiana kolorów, izolacja partii kontrolnych, zgodność środowiska i zamykanie SQLite |
| Interpretacja wyników | `unit/analysis/test_research_report.py` | Perspektywa koloru agenta, przerwania bez punktów, pełne pary, niepewność i próg przewagi |
| Pełna kampania | `integration/test_research_campaign.py` | Cztery metody, restart, ocena przed i po treningu, przerwanie procesu, wznowienie i odczyt legalnych PGN z właściwym FEN |
| GUI kampanii | `integration/test_campaign_gui.py` | Ruch w workerze, ponowne wczytanie i rzeczywisty proces oceny/turnieju |
| GUI swobodnej gry | `integration/test_gui_smoke.py` | Nawigacja, odpowiedź bota, brak blokowania wątku GUI i ochrona zamknięcia podczas obliczeń |
| Paczka Windows | `../scripts/smoke_desktop.py` | Osobny test zbudowanego EXE: GUI, CLI, ocena, wznowienie, eksporty i sprzątanie katalogu tymczasowego |

## Uruchomienie

Z katalogu repozytorium:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
venv/Scripts/python.exe -m pytest -q
venv/Scripts/python.exe -m pytest -q tests/unit/learning tests/unit/analysis/test_research_report.py tests/unit/experiments/test_research.py tests/integration/test_research_campaign.py
```

Ruff i mypy uruchamia się osobno. `ai-dev check --mode fast` sprawdza lint i typy, ale nie zastępuje pełnego pytest. Test paczki wymaga wcześniejszej budowy — patrz `docs/desktop.md`.

Weryfikacja 15 września 2026 po uzupełnieniu testów: **323 passed** (15.26 s). Dodano 23 przypadki względem poprzedniego zestawu 300; istniejące testy przeniesiono bez usuwania scenariuszy do odpowiednich katalogów. Wynik nie oznacza zmierzonego pokrycia 100%.

Aktualizacja UX: testy w `integration/test_campaign_gui.py` obejmują wybór kampanii przed planszą, widoczny ruch człowieka przed pauzą, opóźnioną odpowiedź bota, podświetlenie ruchu oraz końcową pozycję i wynik (mat/pat), które nie znikają bez kliknięcia następnej gry. Testy kampanii sprawdzają również zgodność ze znaną poprzednią paczką i odrzucenie nieznanej wersji źródeł.

Ustawienia i raporty: `integration/test_preferences_and_reports.py` sprawdza trwały zapis preferencji, start pełnoekranowy, przełączanie języka i motywu, zachowanie ekranu kampanii, renderowanie Markdown, ukrycie danych technicznych oraz rzeczywisty pełny zestaw eksperymentów z GUI bez odziedziczonego PYTHONPATH. `unit/ui/test_results_presenter.py` sprawdza rozróżnienie przerwań od remisów i bezpieczne wyświetlanie nazw. Test paczki wykonuje także pełny zestaw eksperymentów i wymaga poprawnego UTF-8 z procesów EXE.
