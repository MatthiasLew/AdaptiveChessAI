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

W menu wybierz **Kampania badawcza**. Utwórz plik kampanii, podaj pseudonim, liczbę partii na agenta i głębokość. Przycisk **Rozpocznij / wznów partię** prowadzi przez naprzemienne gry z AdaptiveMinimax i StaticMinimax. Kolory zmieniają się co rundę. Static jest kontrolą i nie uczy się.

Każdy ruch zapisuje się automatycznie w SQLite. Po ponownym uruchomieniu wczytaj ten sam plik kampanii i wznów partię. Po zakończeniu treningu uruchom turniej: Static, Adaptive przed treningiem i Adaptive po treningu. Modele w turnieju nie uczą się. Raport Markdown, tabela CSV, dane JSON i partie PGN zapisują się obok pliku kampanii.

[Instrukcja kampanii](docs/campaign.md) · [Lista dalszych prac](docs/TODO.md) · [Architektura](docs/architecture.md)

## Aktualny zakres

- GUI z grą swobodną, kampanią, eksperymentami, wynikami i ustawieniami.
- Reguły python-chess, RandomBot, StaticMinimaxBot i AdaptiveMinimaxBot.
- Trwały profil przeciwnika **w kampanii**, checkpoint po każdej ukończonej partii Adaptive.
- W kampanii: ruch bota w tle, promocja, poddanie, automatyczny zapis i wznowienie.
- Turniej 18 partii na trzech otwarciach, ze zmianą kolorów i zapisem po każdej partii.
- Dotychczasowe skrypty bot–bot, CSV/JSON, statystyki i wykresy.

Gra swobodna oraz starsze skrypty eksperymentów pozostają oddzielnymi trybami; nie trenują zapisanych agentów kampanii. Metody imitacji i TD oraz krzywe uczenia są w planie. Obecny adaptive to adaptacja heurystyczna, nie model neuronowy.

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
