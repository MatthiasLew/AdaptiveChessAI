# Tryb człowiek vs bot

Ten dokument opisuje aktualny stan trybu człowiek vs bot w projekcie AdaptiveChessAI.

Na tym etapie projekt nie posiada jeszcze GUI. Istnieje jednak warstwa sesji gry człowieka z botem oraz prosty terminalowy smoke test.

---

## Aktualny zakres

Obecnie dostępne są:

- `HumanVsBotSession`,
- obsługa koloru człowieka,
- obsługa koloru bota,
- wykonywanie ruchów człowieka w notacji UCI,
- automatyczna odpowiedź bota,
- historia ruchów,
- aktualny FEN,
- status gry,
- terminalowy tryb testowy.

---

## Klasa sesji

Główna klasa:

```text
src/adaptive_chess/play/human_vs_bot_session.py
```

Odpowiada za logikę pojedynczej partii człowiek vs bot.

GUI w przyszłości powinno korzystać z tej klasy zamiast bezpośrednio zarządzać planszą i botami.

---

## Terminalowy smoke test

Uruchomienie gry człowiek vs bot w terminalu:

```powershell
python scripts/play_human_vs_bot_terminal.py --bot random --human-color white
```

Dostępne boty:

```text
random
static
adaptive
```

Przykład z botem minimaxowym:

```powershell
python scripts/play_human_vs_bot_terminal.py --bot static --human-color white --depth 1
```

Przykład z botem adaptacyjnym:

```powershell
python scripts/play_human_vs_bot_terminal.py --bot adaptive --human-color black --depth 1
```

---

## Format ruchów

Ruchy wpisuje się w notacji UCI.

Przykłady:

```text
e2e4
g1f3
e7e8q
```

Wyjście z gry:

```text
quit
```

---

## Znaczenie przed GUI

Ten etap jest potrzebny, ponieważ GUI nie powinno implementować logiki gry.

Docelowy przepływ:

```text
GUI
 ↓
HumanVsBotSession
 ↓
Game + Boty
 ↓
python-chess
```

Dzięki temu GUI będzie odpowiadało tylko za:

- rysowanie planszy,
- przyjmowanie kliknięć,
- wyświetlanie historii,
- wyświetlanie statusu.

Logika gry pozostaje testowalna bez GUI.

---

## Minimalne kryterium gotowości przed GUI

Warstwa przed GUI jest gotowa, jeśli:

- testy `HumanVsBotSession` przechodzą,
- terminalowy smoke test działa,
- człowiek może wykonać ruch,
- bot odpowiada ruchem,
- historia ruchów jest aktualizowana,
- status gry jest dostępny,
- FEN jest aktualizowany.