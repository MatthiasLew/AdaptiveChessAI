# Roadmap GUI i trybu człowiek vs bot

Ten dokument opisuje plan przejścia od backendu badawczego do właściwej aplikacji z GUI.

---

## Cel fazy GUI

Celem jest dodanie aplikacji, w której użytkownik może:

- uruchomić okno programu,
- wybrać bota,
- wybrać kolor,
- wybrać głębokość minimaxa,
- rozegrać partię przeciwko botowi,
- widzieć szachownicę,
- klikać figury,
- widzieć historię ruchów,
- widzieć status gry,
- zresetować partię,
- zapisać dane z partii.

---

## Aktualny problem

Projekt ma mechanikę, ale nie ma jeszcze warstwy użytkownika.

Obecnie użytkownik może uruchamiać skrypty eksperymentalne, ale nie może normalnie zagrać partii w aplikacji.

---

## Proponowana architektura

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

GUI nie powinno bezpośrednio implementować zasad szachów.

GUI powinno tylko:

- wyświetlać planszę,
- odbierać kliknięcia,
- przekazywać ruchy do sesji,
- odświeżać widok,
- wyświetlać status gry.

Logika gry powinna być w klasie sesji.

---

## Etap 43 — HumanVsBotSession

Pierwszy krok to klasa bez GUI:

```text
src/adaptive_chess/play/human_vs_bot_session.py
```

Odpowiedzialność:

- przechowywać stan partii,
- wiedzieć, jaki kolor ma człowiek,
- wiedzieć, jaki kolor ma bot,
- przyjmować ruch człowieka,
- sprawdzać legalność ruchu,
- wykonywać odpowiedź bota,
- zwracać aktualny FEN,
- zwracać historię ruchów,
- zwracać status gry.

Ten etap trzeba zrobić przed GUI, żeby interfejs nie mieszał się z logiką.

---

## Etap 44 — terminalowy smoke test

Po dodaniu `HumanVsBotSession` należy dodać prosty skrypt:

```text
scripts/play_human_vs_bot_terminal.py
```

Minimalny flow:

```text
użytkownik wpisuje e2e4
system wykonuje ruch
bot odpowiada
system pokazuje FEN i historię ruchów
```

To pozwala sprawdzić logikę człowiek vs bot bez GUI.

---

## Etap 45 — wybór biblioteki GUI

Rekomendowana biblioteka:

```text
PySide6
```

Powody:

- dobrze pasuje do aplikacji desktopowej,
- umożliwia normalne okna, przyciski, listy i panele,
- wygląda bardziej aplikacyjnie niż terminal,
- nadaje się do pracy inżynierskiej.

Alternatywa:

```text
pygame
```

`pygame` jest prostszy do rysowania planszy, ale gorszy do standardowego interfejsu aplikacji.

---

## Etap 46 — podstawowe okno aplikacji

Minimalne okno powinno zawierać:

- tytuł aplikacji,
- miejsce na szachownicę,
- panel boczny,
- przycisk resetu,
- status gry.

---

## Etap 47 — widok szachownicy

Szachownica powinna:

- pokazywać 64 pola,
- pokazywać figury,
- odświeżać się po ruchu,
- obsługiwać orientację białych i czarnych.

Na początku figury mogą być oznaczone literami, np.:

```text
P, N, B, R, Q, K
p, n, b, r, q, k
```

Dopiero później można dodać grafiki figur.

---

## Etap 48 — klikanie figur

Minimalna obsługa:

1. Kliknięcie pola z własną figurą wybiera figurę.
2. Kliknięcie pola docelowego próbuje wykonać ruch.
3. Jeśli ruch jest legalny, następuje ruch człowieka.
4. Po ruchu człowieka odpowiada bot.
5. Widok planszy się odświeża.

---

## Etap 49 — wybór bota

GUI powinno pozwalać wybrać:

- `RandomBot`,
- `StaticMinimaxBot`,
- `AdaptiveMinimaxBot`.

Dodatkowo:

- głębokość minimaxa,
- kolor gracza,
- limit półruchów, opcjonalnie.

---

## Etap 50 — historia ruchów i status gry

Panel boczny powinien pokazywać:

- listę ruchów,
- aktualną turę,
- status gry,
- informację o szachu,
- wynik po zakończeniu partii.

---

## Etap 51 — zapis partii użytkownika

Po partii można zapisać:

- historię ruchów,
- końcowy FEN,
- wynik,
- nazwę bota,
- kolor gracza,
- datę rozegrania.

Format początkowy:

```text
CSV albo JSON
```

---

## Etap 52 — dokumentacja GUI

Po dodaniu GUI trzeba uzupełnić dokumentację:

- jak uruchomić aplikację,
- jak wybrać bota,
- jak grać,
- jak zapisywane są partie,
- jakie są ograniczenia GUI.

---

## Minimalne kryterium aplikacyjnego MVP

Aplikacyjne MVP będzie można uznać za gotowe dopiero wtedy, gdy użytkownik będzie mógł:

- uruchomić aplikację,
- zobaczyć szachownicę,
- wykonać legalny ruch,
- dostać odpowiedź bota,
- dokończyć albo zresetować partię,
- zobaczyć wynik lub status gry.

Do tego momentu projekt nie powinien być opisywany jako domknięta aplikacja.

## Status realizacji przed GUI

| Etap | Status |
|---|---|
| HumanVsBotSession | wykonane |
| terminalowy smoke test | wykonane |
| dokumentacja trybu człowiek vs bot | wykonane |
| GUI | następny etap |