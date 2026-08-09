# Aktualny status projektu AdaptiveChessAI

Ten dokument opisuje rzeczywisty status projektu AdaptiveChessAI po zakończeniu fazy mechaniczno-badawczej.

Ważna korekta: projekt nie jest jeszcze domkniętym MVP aplikacji. Domknięta jest tylko część backendowa i badawcza.

---

## Status ogólny

```text
Backend badawczy: gotowy w wersji roboczej
Silnik eksperymentów: gotowy
Boty: gotowe w wersji roboczej
Analiza wyników: gotowa w wersji roboczej
GUI: brak
Tryb człowiek vs bot: brak
Aplikacyjne MVP: niedomknięte
```

---

## Co projekt miał robić docelowo

Docelowo projekt ma być aplikacją pozwalającą:

- uruchomić program z interfejsem użytkownika,
- wybrać bota,
- wybrać kolor gracza,
- rozegrać partię człowiek vs bot,
- obserwować ruchy na szachownicy,
- zapisywać dane z partii,
- analizować, jak boty adaptują się do stylu gry użytkownika,
- porównywać skuteczność różnych botów.

Tego zakresu projekt jeszcze w pełni nie spełnia, ponieważ nie ma GUI i trybu gry użytkownika z botem.

---

## Co obecnie działa

### Mechanika gry

Projekt posiada mechanikę obsługi partii opartą na `python-chess`.

Dostępne są:

- plansza,
- legalne ruchy,
- wykonywanie ruchów,
- wykrywanie końca gry,
- wynik partii,
- końcowy FEN.

---

### Boty

Obecnie zaimplementowano:

| Bot | Status | Opis |
|---|---|---|
| `RandomBot` | działa | wybiera losowy legalny ruch |
| `StaticMinimaxBot` | działa | korzysta z minimaxa i alfa-beta pruning |
| `AdaptiveMinimaxBot` | działa | korzysta z minimaxa oraz profilu przeciwnika |

Bot adaptacyjny potrafi obserwować ruchy przeciwnika i używać prostego profilu przy ocenie ruchów.

---

### Eksperymenty bot vs bot

Projekt pozwala uruchamiać eksperymenty:

- `RandomBot vs RandomBot`,
- `RandomBot vs StaticMinimaxBot`,
- `RandomBot vs AdaptiveMinimaxBot`,
- `StaticMinimaxBot vs AdaptiveMinimaxBot`.

Te eksperymenty są użyteczne do części badawczej pracy, ale nie zastępują aplikacji z GUI.

---

### Eksport i analiza danych

Projekt obsługuje:

- eksport CSV,
- eksport metadanych JSON,
- raporty tekstowe,
- wykresy PNG,
- zbiorcze podsumowanie eksperymentów.

To jest wartościowa część badawcza projektu.

---

## Czego obecnie brakuje

Najważniejsze braki względem docelowej aplikacji:

| Obszar | Status |
|---|---|
| GUI | brak |
| szachownica w oknie aplikacji | brak |
| klikanie figur | brak |
| wybór bota z poziomu aplikacji | brak |
| wybór koloru gracza | brak |
| człowiek vs bot | brak |
| historia ruchów w interfejsie | brak |
| komunikaty o stanie gry | brak |
| reset partii w GUI | brak |
| zapis partii użytkownika | brak |
| analiza partii użytkownika | brak |

---

## Poprawna interpretacja aktualnego projektu

Aktualny projekt należy opisywać tak:

```text
Projekt posiada działający backend badawczy i mechanikę eksperymentów.
Projekt nie posiada jeszcze warstwy aplikacyjnej z GUI.
Projekt wymaga kolejnej fazy prac obejmującej tryb człowiek vs bot oraz interfejs graficzny.
```

Nie należy pisać:

```text
MVP projektu jest domknięte.
```

Poprawniejszy zapis:

```text
Domknięta jest robocza wersja backendu badawczego.
Aplikacyjne MVP nie jest jeszcze domknięte.
```

---

## Dlaczego obecny etap nadal ma wartość

Mimo braku GUI projekt ma już ważną bazę:

- boty są testowalne,
- mechanika gry jest odseparowana od przyszłego GUI,
- eksperymenty można uruchamiać automatycznie,
- wyniki są zapisywane w plikach,
- można analizować zachowanie botów,
- istnieje fundament pod podłączenie GUI.

Dzięki temu GUI nie musi implementować logiki szachowej od zera. Powinno tylko korzystać z istniejących klas i mechanizmów.

---

## Najbliższa faza prac

Następna faza to:

```text
GUI i tryb człowiek vs bot
```

Zalecana kolejność:

1. Dodać `HumanVsBotSession`.
2. Dodać testy dla sesji człowiek vs bot.
3. Dodać prosty terminalowy smoke test.
4. Wybrać bibliotekę GUI.
5. Dodać podstawowe okno.
6. Dodać widok szachownicy.
7. Dodać klikanie figur.
8. Dodać odpowiedź bota.
9. Dodać wybór bota i parametrów.
10. Dodać historię ruchów i status gry.

---

## Decyzja na teraz

Przed dalszym rozwojem należy uporządkować dokumentację i usunąć pliki sugerujące, że projekt jest finalnie domknięty.

Po tej korekcie można rozpocząć kolejną fazę:

```text
Etap 43 — HumanVsBotSession bez GUI
```