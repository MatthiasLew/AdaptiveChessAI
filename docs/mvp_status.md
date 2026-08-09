# Status MVP projektu AdaptiveChessAI

Ten dokument podsumowuje aktualny stan projektu AdaptiveChessAI oraz plan domknięcia wersji MVP do pracy inżynierskiej.

Projekt dotyczy implementacji platformy do analizy skuteczności botów szachowych, w tym botów adaptacyjnych uczących się cech stylu przeciwnika.

---

## Cel projektu

Celem projektu jest przygotowanie aplikacji badawczej pozwalającej:

- uruchamiać partie szachowe między różnymi botami,
- porównywać boty statyczne i adaptacyjne,
- zapisywać wyniki eksperymentów,
- generować raporty oraz wykresy,
- analizować, czy prosta adaptacja do stylu przeciwnika wpływa na skuteczność gry.

Projekt nie ma na celu stworzenia silnika szachowego konkurującego z profesjonalnymi programami typu Stockfish. Celem jest platforma badawcza i porównawcza.

---

## Aktualny zakres MVP

Na obecnym etapie projekt zawiera działający fundament MVP.

### Obsługa gry

Zaimplementowano podstawową warstwę obsługi partii:

- opakowanie planszy `python-chess`,
- wykonywanie legalnych ruchów,
- kontrolę stanu gry,
- wykrywanie zakończenia partii,
- wynik formalny partii.

Główna odpowiedzialność tej warstwy to oddzielenie logiki rozgrywki od logiki botów.

---

### Boty

Projekt zawiera trzy główne typy botów:

| Bot | Charakterystyka |
|---|---|
| `RandomBot` | wybiera losowy legalny ruch |
| `StaticMinimaxBot` | używa minimaxa z alfa-beta pruning |
| `AdaptiveMinimaxBot` | używa minimaxa oraz profilu przeciwnika |

`RandomBot` pełni rolę prostego punktu odniesienia.

`StaticMinimaxBot` jest klasycznym botem nieadaptacyjnym.

`AdaptiveMinimaxBot` zbiera informacje o przeciwniku i używa ich jako korekty przy ocenie ruchów.

---

### Funkcja oceny pozycji

Aktualna funkcja oceny pozycji uwzględnia:

- materiał,
- mobilność,
- kontrolę centrum,
- mata,
- remisy.

Wersja funkcji oceny jest zapisywana w metadanych eksperymentu, co ułatwia powtarzalność badań.

---

### Minimax i alfa-beta pruning

Zaimplementowano:

- podstawowy minimax,
- minimax z alfa-beta pruning,
- wybór najlepszego ruchu na podstawie oceny pozycji,
- testy poprawności wyboru ruchów.

Alfa-beta pruning pozwala ograniczyć liczbę analizowanych gałęzi drzewa gry bez zmiany wyniku minimaxa.

---

### Adaptacja

Aktualny mechanizm adaptacji obejmuje:

- obserwowanie ruchów przeciwnika,
- zliczanie cech ruchów przeciwnika,
- trwały profil przeciwnika na poziomie serii partii,
- korektę oceny ruchu na podstawie profilu przeciwnika,
- eksport końcowych profili do metadanych JSON.

Profil przeciwnika zapisuje między innymi:

- liczbę obserwowanych ruchów,
- liczbę bić,
- liczbę szachów,
- liczbę ruchów do centrum,
- współczynnik bić,
- współczynnik szachów,
- współczynnik ruchów do centrum.

---

### Eksperymenty

Projekt zawiera skrypty do uruchamiania głównych eksperymentów:

- `RandomBot vs RandomBot`,
- `RandomBot vs StaticMinimaxBot`,
- `RandomBot vs AdaptiveMinimaxBot`,
- `StaticMinimaxBot vs AdaptiveMinimaxBot`.

Eksperymenty obsługują:

- liczbę partii,
- limit półruchów,
- głębokość minimaxa,
- próg adjudykacji materiałowej,
- eksport CSV,
- eksport metadanych JSON.

---

### Wyniki formalne i techniczne

Każda partia zapisuje dwa typy wyniku:

| Pole | Znaczenie |
|---|---|
| `result` | formalny wynik partii |
| `adjudicated_result` | wynik techniczny po adjudykacji materiałowej |

Wynik techniczny pozwala sensowniej analizować partie przerwane limitem półruchów.

Jeśli partia zakończy się limitem, a jedna ze stron ma przewagę materiałową przekraczającą ustalony próg, wynik techniczny może zostać przypisany tej stronie.

---

### Eksport danych

Projekt obsługuje eksport:

- szczegółowych wyników partii do CSV,
- metadanych eksperymentów do JSON,
- raportów tekstowych,
- wykresów PNG.

CSV zawiera między innymi:

- nazwę eksperymentu,
- numer partii,
- nazwy botów,
- wynik formalny,
- wynik techniczny,
- powód zakończenia,
- liczbę półruchów,
- końcową przewagę materiałową,
- historię ruchów,
- historię przewagi materiałowej,
- historię ocen pozycji,
- końcowy FEN.

---

### Analiza wyników

Projekt zawiera moduł analityczny pozwalający:

- wczytać CSV,
- pogrupować wyniki po eksperymentach,
- policzyć wyniki formalne,
- policzyć wyniki techniczne,
- policzyć średnią długość partii,
- policzyć średnią końcową przewagę materiałową,
- policzyć liczbę partii zakończonych limitem,
- wygenerować raport tekstowy.

---

### Wykresy

Projekt generuje wykresy:

- wyników technicznych,
- średniej końcowej przewagi materialnej,
- liczby partii zakończonych limitem.

Wykresy są zapisywane jako pliki PNG.

---

### Pełny pipeline eksperymentalny

Projekt zawiera zbiorczy skrypt:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Skrypt uruchamia pełny zestaw eksperymentów i generuje:

- CSV,
- metadane JSON,
- raporty tekstowe,
- wykresy.

Dzięki temu pełny proces badawczy może być uruchomiony jedną komendą.

---

## Co obecnie można uznać za działające MVP

Za działające MVP można uznać następujący zakres:

- działające boty: losowy, minimaxowy i adaptacyjny,
- możliwość rozgrywania pojedynczych partii,
- możliwość rozgrywania serii partii,
- możliwość porównywania głównych botów,
- wynik formalny i techniczny,
- eksport wyników do CSV,
- eksport metadanych do JSON,
- trwały profil przeciwnika w seriach adaptacyjnych,
- raporty tekstowe,
- wykresy,
- pełny skrypt uruchamiający pipeline eksperymentalny,
- testy jednostkowe dla głównych komponentów.

To jest wystarczający fundament do rozpoczęcia części badawczej pracy inżynierskiej.

---

## Najważniejsze ograniczenia aktualnej wersji

Aktualna wersja ma kilka świadomych ograniczeń.

### Brak GUI

Projekt działa przez skrypty terminalowe. GUI nie jest wymagane do części badawczej MVP.

Możliwe rozszerzenie:

- prosty interfejs do ręcznego grania przeciwko botowi,
- podgląd planszy,
- wybór bota i głębokości.

Nie jest to konieczne do domknięcia MVP badawczego.

---

### Prosta adaptacja

Adaptacja ma charakter heurystyczny.

Bot nie używa jeszcze pełnego uczenia maszynowego. Obecny mechanizm bazuje na:

- ręcznie dobranych cechach,
- prostym profilu przeciwnika,
- małej korekcie oceny ruchu.

Jest to jednak wystarczające do pokazania różnicy między botem statycznym i adaptacyjnym.

---

### Prosta funkcja oceny

Funkcja oceny uwzględnia materiał, mobilność i centrum, ale nie obejmuje jeszcze bardziej zaawansowanych elementów, takich jak:

- bezpieczeństwo króla,
- struktura pionów,
- rozwój figur,
- izolowane piony,
- podwojone piony,
- otwarte linie,
- tempo,
- tablice pól figur.

Te elementy można dodać jako rozszerzenia, ale nie są konieczne do minimalnego MVP.

---

### Brak pełnej bazy danych

Wyniki są zapisywane do CSV i JSON. To jest wystarczające dla MVP.

Baza danych, np. SQLite, może być późniejszym rozszerzeniem, jeśli projekt ma przechowywać większą liczbę eksperymentów albo umożliwiać przeszukiwanie wyników.

---

### Ograniczona siła gry

Bot minimaxowy przy niskiej głębokości nie gra bardzo silnie. To jest oczekiwane.

Projekt nie mierzy siły silnika szachowego względem profesjonalnych programów, tylko porównuje konfiguracje botów w ramach jednej platformy.

---

## Plan domknięcia MVP

Do pełnego domknięcia MVP zalecane są następujące kroki.

### 1. Uruchomić pełny zestaw testów

```powershell
python -m pytest
```

Wynik powinien być zielony przed generowaniem danych badawczych.

---

### 2. Uruchomić szybki pełny eksperyment testowy

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_test --matches 2 --max-half-moves 20 --depths 1
```

Celem jest sprawdzenie, czy pipeline działa od początku do końca.

---

### 3. Uruchomić pierwszy właściwy zestaw wyników

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

To jest rozsądny pierwszy zestaw danych do opisania w pracy.

---

### 4. Sprawdzić metadane eksperymentów adaptacyjnych

Należy sprawdzić, czy pliki:

```text
random_vs_adaptive.metadata.json
static_vs_adaptive.metadata.json
```

zawierają pole:

```text
adaptive_profile_snapshots
```

To potwierdza, że profile przeciwnika zostały zapisane.

---

### 5. Zweryfikować raporty i wykresy

Po uruchomieniu pełnego pipeline’u należy sprawdzić:

- czy powstały raporty `.txt`,
- czy powstały wykresy `.png`,
- czy wykresy zawierają dane,
- czy wyniki formalne i techniczne są rozróżnione.

---

### 6. Opisać wyniki w pracy

W pracy należy opisać:

- konfigurację eksperymentów,
- liczbę partii,
- limit półruchów,
- głębokość minimaxa,
- próg adjudykacji,
- wersję funkcji oceny,
- różnice między botami,
- wyniki formalne i techniczne,
- profile przeciwnika dla botów adaptacyjnych.

---

## Proponowany minimalny zestaw eksperymentów do pracy

Minimalny zestaw danych badawczych:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Opcjonalny zestaw porównawczy dla głębokości `2`:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_depth2 --matches 3 --max-half-moves 60 --depths 2
```

Nie należy zaczynać od dużej liczby partii dla `depth=2`, ponieważ czas działania może być znacznie dłuższy.

---

## Proponowany zakres dalszych etapów

Po domknięciu MVP można rozważyć następujące rozszerzenia:

1. Dodanie prostego GUI.
2. Dodanie SQLite jako trwałej bazy wyników.
3. Rozbudowanie funkcji oceny pozycji.
4. Dodanie bardziej zaawansowanego profilu przeciwnika.
5. Dodanie kilku wariantów bota adaptacyjnego.
6. Dodanie testów wydajnościowych.
7. Dodanie eksportu raportu do PDF.
8. Dodanie wykresów porównujących wiele uruchomień eksperymentów.

Te elementy nie są wymagane do minimalnego MVP, ale mogą zwiększyć wartość projektu.

---

## Aktualny wniosek projektowy

Projekt osiągnął etap kompletnego MVP badawczego.

Najważniejsze komponenty są obecne:

- rozgrywanie partii,
- boty bazowe,
- bot adaptacyjny,
- eksperymenty,
- eksport danych,
- analiza wyników,
- wykresy,
- metadane,
- dokumentacja uruchamiania.

Kolejne prace powinny skupić się na:

1. stabilizacji,
2. uruchomieniu właściwych eksperymentów,
3. analizie wyników,
4. opisaniu implementacji i wyników w pracy inżynierskiej.