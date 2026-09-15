# AdaptiveChessAI

Aplikacja desktopowa PySide6 do badania adaptacji agentów szachowych na podstawie partii z graczem nieeksperckim. Projekt pracy inżynierskiej.

## Uruchomienie

W katalogu repozytorium, na Windows (zweryfikowano Python 3.13):

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe scripts/run_gui.py
```

## Kampania badawcza

W menu wybierz **Graj**, a następnie **Nowa kampania** albo **Wczytaj kampanię…**. Ustal X partii na metodę i budżet wyszukiwania. Zagraj 4X partii: z agentem profilowym, imitacją, TD i kontrolą statyczną. Autosave pozwala wrócić do gry po restarcie.

**Oceń checkpointy / turniej** porównuje wszystkie zapisane modele ze stałą kontrolą, a po treningu rozgrywa turniej czterech metod (domyślnie 36 meczów). Osobne partie kontrolne przeciw człowiekowi nie uczą agentów. Raport zawiera krzywe uczenia, przedziały, koszty obliczeń i eksport CSV/JSON/PGN.

[Instrukcja i protokół badania](docs/campaign.md) · [Stan zadań](docs/TODO.md) · [Architektura](docs/architecture.md) · [Paczka Windows](docs/desktop.md)

Metody imitacji i TD są małymi modelami liniowymi ze wspólną oceną szachową. To platforma do pomiaru skuteczności, nie obietnica, że uczenie pokona gracza. Przewaga nad człowiekiem wymaga rzeczywistych partii kontrolnych.

## Testy

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\venv\Scripts\python.exe -m pytest
```

Narzędzia jakości: `ruff check .` i `mypy src scripts tests` po zainstalowaniu Ruff/mypy w środowisku narzędzi deweloperskich.

## Eksperymenty skryptowe

```powershell
.\venv\Scripts\python.exe scripts/run_full_experiment_suite.py --output-dir results/smoke --matches 2 --max-half-moves 20 --depths 1
.\venv\Scripts\python.exe scripts/run_campaign_tournament.py data/campaigns/moje_badanie.sqlite3
```

Starszy pipeline opisuje [dokumentacja eksperymentów](docs/experiments.md). Jego techniczne remisy i adjudykacja nie są protokołem nowej kampanii. Mała seria testowa nie stanowi dowodu skuteczności uczenia.

## Wygląd i obsługa

Program domyślnie uruchamia się na pełnym ekranie. **F11** przełącza pełny ekran, a **Esc** wraca do zmaksymalizowanego okna. W **Ustawieniach** można zapisać język interfejsu (polski/angielski), motyw jasny/ciemny, start na pełnym ekranie i pauzę przed odpowiedzią bota (300–3000 ms).

**Wyniki** pokazują podsumowanie i tabele partii oraz podgląd wykresów. Dane JSON i raporty techniczne są ukryte do zaznaczenia **Pokaż pliki techniczne**. Zapisane raporty i logi zachowują język ich źródła. Partie zatrzymane limitem są przedstawiane osobno, także gdy stary plik CSV zapisywał je jako remisy.

**Eksperymenty** służą automatycznym porównaniom botów. Wybierz porównanie i liczbę partii, uruchom je i odczytaj podsumowanie na ekranie. Diagnostyka jest dostępna po zaznaczeniu **Szczegóły techniczne**. Do treningu agentów z własnych partii nadal służy **Graj**.
