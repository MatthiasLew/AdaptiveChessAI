# AdaptiveChessAI

AdaptiveChessAI to projekt pracy inżynierskiej dotyczący platformy do analizy skuteczności botów szachowych, w tym botów adaptacyjnych uczących się wybranych cech stylu przeciwnika.

Aktualny stan projektu obejmuje przede wszystkim backend badawczy, mechanikę rozgrywania partii, boty, eksperymenty, eksport wyników oraz analizę danych.

Projekt nie posiada jeszcze właściwego GUI i nie umożliwia jeszcze wygodnej gry człowieka z botami w aplikacji okienkowej.

---

## Aktualny status

```text
Backend badawczy: działa
Mechanika botów: działa
Eksperymenty bot vs bot: działają
Eksport CSV/JSON: działa
Raporty i wykresy: działają
GUI: brak
Tryb człowiek vs bot: brak
Aplikacyjne MVP: niedomknięte
```

Szczegółowy status projektu znajduje się w:

```text
docs/mvp_status.md
```

Plan dalszych prac nad GUI znajduje się w:

```text
docs/gui_roadmap.md
```

---

## Co obecnie działa

Projekt zawiera:

- obsługę partii szachowej przez `python-chess`,
- bazową klasę botów,
- `RandomBot`,
- `StaticMinimaxBot`,
- `AdaptiveMinimaxBot`,
- minimax,
- alfa-beta pruning,
- funkcję oceny pozycji,
- profil przeciwnika dla bota adaptacyjnego,
- rozgrywanie pojedynczych partii,
- rozgrywanie serii partii,
- eksperymenty bot vs bot,
- eksport wyników do CSV,
- eksport metadanych do JSON,
- raporty tekstowe,
- wykresy PNG,
- zbiorcze podsumowanie eksperymentów.

---

## Czego jeszcze brakuje

Najważniejsze brakujące elementy:

- GUI,
- widok szachownicy,
- klikanie figur,
- tryb człowiek vs bot,
- wybór bota w aplikacji,
- wybór koloru gracza,
- historia ruchów w GUI,
- komunikaty o szachu, macie i remisie,
- reset partii z poziomu aplikacji,
- zapis partii użytkownika,
- wykorzystanie danych z partii użytkownika w analizie.

---

## Instalacja zależności

```powershell
pip install -r requirements.txt
```

---

## Testy

```powershell
python -m pytest
```

---

## Eksperymenty

Projekt zawiera skrypty do uruchamiania eksperymentów porównujących boty szachowe:

- `RandomBot`,
- `StaticMinimaxBot`,
- `AdaptiveMinimaxBot`.

Podstawowy zestaw eksperymentów backendowych można uruchomić komendą:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Skrypt generuje:

- pliki CSV z wynikami partii,
- pliki metadanych JSON,
- raporty tekstowe,
- wykresy PNG,
- zbiorcze podsumowanie Markdown.

Szczegółowy opis uruchamiania eksperymentów znajduje się w:

```text
docs/experiments.md
```

---

## Kierunek dalszego rozwoju

Najbliższy właściwy kierunek prac to GUI oraz możliwość gry człowieka z botami.

Planowana kolejność:

1. `HumanVsBotSession` bez GUI.
2. Terminalowy test człowiek vs bot.
3. Dodanie zależności GUI.
4. Podstawowe okno aplikacji.
5. Widok szachownicy.
6. Klikanie figur.
7. Ruch bota po ruchu gracza.
8. Wybór bota, koloru i głębokości.
9. Historia ruchów i status gry.
10. Zapis partii użytkownika.

---

## Decyzja projektowa

Aktualnie projekt nie powinien być opisywany jako domknięta aplikacja.

Poprawna interpretacja:

```text
Projekt ma gotowy mechaniczny fundament badawczy.
Projekt nie ma jeszcze kompletnego MVP aplikacyjnego.
Następna faza to GUI i tryb człowiek vs bot.
```