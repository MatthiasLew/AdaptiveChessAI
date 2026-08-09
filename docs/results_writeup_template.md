# Szablon opisu wyników eksperymentów

Ten dokument zawiera szablon opisu wyników eksperymentów do pracy inżynierskiej.

Tekst należy traktować jako bazę do uzupełnienia po uruchomieniu finalnego zestawu eksperymentów.

---

## 1. Cel eksperymentów

Celem eksperymentów było porównanie skuteczności kilku typów botów szachowych zaimplementowanych w projekcie AdaptiveChessAI.

Porównano następujące boty:

- `RandomBot`,
- `StaticMinimaxBot`,
- `AdaptiveMinimaxBot`.

Szczególną uwagę zwrócono na porównanie bota statycznego i adaptacyjnego. Oba boty wykorzystują mechanizm minimax z alfa-beta pruning, jednak bot adaptacyjny dodatkowo gromadzi profil przeciwnika i wykorzystuje go przy ocenie ruchów.

---

## 2. Konfiguracja eksperymentów

Eksperymenty uruchomiono za pomocą zbiorczego skryptu:

```powershell
python scripts/run_full_experiment_suite.py --output-dir results/full_suite_v1 --matches 10 --max-half-moves 80 --depths 1
```

Parametry eksperymentu:

| Parametr | Wartość |
|---|---:|
| liczba partii na konfigurację | 10 |
| limit półruchów | 80 |
| głębokość minimaxa | 1 |
| próg adjudykacji materiałowej | 3 |

Wyniki zapisano w katalogu:

```text
results/full_suite_v1/
```

---

## 3. Opis porównywanych botów

### RandomBot

`RandomBot` wybiera losowy legalny ruch z aktualnej pozycji. Bot ten nie analizuje pozycji i nie wykorzystuje historii partii. W eksperymentach pełni funkcję punktu odniesienia.

### StaticMinimaxBot

`StaticMinimaxBot` wybiera ruch na podstawie algorytmu minimax z alfa-beta pruning. Do oceny pozycji wykorzystuje funkcję uwzględniającą materiał, mobilność oraz kontrolę centrum. Bot nie modyfikuje swojego zachowania na podstawie wcześniejszych ruchów przeciwnika.

### AdaptiveMinimaxBot

`AdaptiveMinimaxBot` bazuje na minimaxie z alfa-beta pruning, ale dodatkowo obserwuje ruchy przeciwnika. Na podstawie obserwacji tworzony jest profil przeciwnika zawierający między innymi częstotliwość bić, szachów oraz ruchów do centrum. Profil ten jest wykorzystywany jako dodatkowa korekta przy ocenie kandydatów ruchu.

---

## 4. Rodzaje wyników

W eksperymentach zapisano dwa rodzaje wyników:

| Rodzaj wyniku | Znaczenie |
|---|---|
| wynik formalny | wynik partii zgodny z zasadami gry albo techniczny remis po limicie |
| wynik techniczny | wynik po adjudykacji materiałowej dla partii przerwanych limitem |

Rozróżnienie tych wyników jest istotne, ponieważ część partii może nie zakończyć się matem ani remisem wynikającym bezpośrednio z zasad gry. W takich przypadkach wynik techniczny pozwala uwzględnić przewagę materialną jednej ze stron.

---

## 5. Wyniki zbiorcze

Zbiorcze podsumowanie wyników znajduje się w pliku:

```text
results/full_suite_v1/suite_summary.md
```

W tabeli uwzględniono:

- nazwę pliku CSV,
- nazwę eksperymentu,
- liczbę partii,
- wyniki formalne,
- wyniki techniczne,
- średnią liczbę półruchów,
- średnią końcową przewagę materialną białych,
- liczbę partii zakończonych limitem.

---

## 6. RandomBot vs RandomBot

Eksperyment `RandomBot vs RandomBot` pełnił funkcję bazową. Jego celem było sprawdzenie zachowania systemu przy dwóch botach, które nie analizują pozycji.

Do uzupełnienia po eksperymencie:

| Metryka | Wartość |
|---|---:|
| liczba partii | do uzupełnienia |
| wygrane białych formalnie | do uzupełnienia |
| wygrane czarnych formalnie | do uzupełnienia |
| remisy formalnie | do uzupełnienia |
| wygrane białych technicznie | do uzupełnienia |
| wygrane czarnych technicznie | do uzupełnienia |
| remisy technicznie | do uzupełnienia |
| średnia liczba półruchów | do uzupełnienia |
| średnia przewaga materialna białych | do uzupełnienia |
| partie zakończone limitem | do uzupełnienia |

Interpretacja:

```text
Do uzupełnienia na podstawie raportu random_series_report.txt oraz suite_summary.md.
```

---

## 7. RandomBot vs StaticMinimaxBot

Eksperyment `RandomBot vs StaticMinimaxBot` służył sprawdzeniu, czy klasyczny bot minimaxowy osiąga lepsze wyniki niż bot losowy.

Do uzupełnienia po eksperymencie:

| Metryka | Wartość |
|---|---:|
| liczba partii | do uzupełnienia |
| wyniki formalne | do uzupełnienia |
| wyniki techniczne | do uzupełnienia |
| średnia liczba półruchów | do uzupełnienia |
| średnia przewaga materialna białych | do uzupełnienia |
| partie zakończone limitem | do uzupełnienia |

Interpretacja:

```text
Do uzupełnienia. Należy sprawdzić, czy StaticMinimaxBot uzyskał przewagę nad RandomBotem oraz czy przewaga jest widoczna w wynikach technicznych i średniej przewadze materialnej.
```

---

## 8. RandomBot vs AdaptiveMinimaxBot

Eksperyment `RandomBot vs AdaptiveMinimaxBot` służył sprawdzeniu, czy bot adaptacyjny radzi sobie lepiej od bota losowego.

Do uzupełnienia po eksperymencie:

| Metryka | Wartość |
|---|---:|
| liczba partii | do uzupełnienia |
| wyniki formalne | do uzupełnienia |
| wyniki techniczne | do uzupełnienia |
| średnia liczba półruchów | do uzupełnienia |
| średnia przewaga materialna białych | do uzupełnienia |
| partie zakończone limitem | do uzupełnienia |

Dodatkowo należy sprawdzić plik:

```text
random_vs_adaptive.metadata.json
```

W szczególności pole:

```text
adaptive_profile_snapshots
```

Interpretacja:

```text
Do uzupełnienia. Należy opisać, jakie cechy przeciwnika zostały zaobserwowane przez profil bota adaptacyjnego oraz czy miały one widoczny związek z wynikiem.
```

---

## 9. StaticMinimaxBot vs AdaptiveMinimaxBot

Ten eksperyment jest najważniejszy dla oceny adaptacji.

Oba boty korzystają z podobnego mechanizmu bazowego:

```text
minimax + alfa-beta pruning + funkcja oceny pozycji
```

Różnica polega na tym, że `AdaptiveMinimaxBot` dodatkowo wykorzystuje profil przeciwnika.

Do uzupełnienia po eksperymencie:

| Metryka | Wartość |
|---|---:|
| liczba partii | do uzupełnienia |
| wyniki formalne | do uzupełnienia |
| wyniki techniczne | do uzupełnienia |
| średnia liczba półruchów | do uzupełnienia |
| średnia przewaga materialna białych | do uzupełnienia |
| partie zakończone limitem | do uzupełnienia |

Dodatkowo należy sprawdzić plik:

```text
static_vs_adaptive.metadata.json
```

W szczególności pole:

```text
adaptive_profile_snapshots
```

Interpretacja:

```text
Do uzupełnienia. Należy ocenić, czy AdaptiveMinimaxBot uzyskał przewagę nad StaticMinimaxBotem, czy wyniki były zbliżone, oraz czy profil przeciwnika zebrał wystarczającą liczbę obserwacji.
```

---

## 10. Analiza profilu przeciwnika

Profil przeciwnika zawiera między innymi:

| Pole | Znaczenie |
|---|---|
| `observed_moves` | liczba zaobserwowanych ruchów przeciwnika |
| `captures` | liczba ruchów będących biciami |
| `checks` | liczba ruchów dających szacha |
| `center_moves` | liczba ruchów na centralne pola |
| `capture_ratio` | udział bić w obserwowanych ruchach |
| `check_ratio` | udział szachów w obserwowanych ruchach |
| `center_move_ratio` | udział ruchów do centrum |

Opis do uzupełnienia:

```text
W eksperymencie zaobserwowano, że profil przeciwnika zgromadził dane dotyczące stylu gry. Najważniejsze wartości to: ...
```

Możliwa interpretacja:

```text
Jeżeli liczba obserwowanych ruchów była niska, wpływ adaptacji mógł być ograniczony. Jeżeli profil zebrał dużo obserwacji, można analizować, czy korekta adaptacyjna wpłynęła na wyniki.
```

---

## 11. Interpretacja wyników formalnych i technicznych

Opis do uzupełnienia:

```text
Wyniki formalne pokazują bezpośrednie zakończenia partii, natomiast wyniki techniczne uwzględniają adjudykację materiałową. Różnice między tymi wynikami wskazują, że część partii została przerwana limitem półruchów, ale jedna ze stron uzyskała przewagę materialną.
```

Należy zwrócić uwagę na:

- liczbę partii zakończonych limitem,
- różnicę między wynikami formalnymi i technicznymi,
- średnią przewagę materialną,
- wpływ koloru na wynik.

---

## 12. Ograniczenia eksperymentu

Eksperymenty mają następujące ograniczenia:

- liczba partii może być zbyt mała do silnych wniosków statystycznych,
- głębokość minimaxa jest niska ze względów wydajnościowych,
- funkcja oceny pozycji jest uproszczona,
- adaptacja ma charakter heurystyczny,
- boty nie korzystają z profesjonalnych bibliotek silnikowych typu Stockfish,
- wyniki zależą od przyjętego limitu półruchów i progu adjudykacji.

---

## 13. Wnioski

Do uzupełnienia po analizie wyników:

```text
Na podstawie przeprowadzonych eksperymentów można stwierdzić, że ...
```

Możliwe warianty wniosku:

```text
AdaptiveMinimaxBot uzyskał lepsze wyniki niż StaticMinimaxBot, co sugeruje, że nawet prosta adaptacja heurystyczna może poprawić skuteczność gry w wybranych konfiguracjach.
```

albo:

```text
AdaptiveMinimaxBot uzyskał wyniki zbliżone do StaticMinimaxBot. Oznacza to, że sama obecność profilu przeciwnika nie gwarantuje poprawy wyników, a skuteczność adaptacji zależy od sposobu wykorzystania zgromadzonych danych.
```

albo:

```text
AdaptiveMinimaxBot uzyskał gorsze wyniki niż StaticMinimaxBot. Może to wskazywać, że zastosowana korekta adaptacyjna była zbyt uproszczona albo zakłócała bazową ocenę minimaxową.
```

---

## 14. Dalsze prace

Możliwe kierunki rozwoju:

- zwiększenie liczby partii,
- testowanie większej głębokości minimaxa,
- rozbudowa funkcji oceny pozycji,
- dodanie bardziej szczegółowego profilu przeciwnika,
- zapis wyników do bazy danych,
- dodanie GUI,
- porównanie kilku wariantów bota adaptacyjnego,
- analiza statystyczna wyników.