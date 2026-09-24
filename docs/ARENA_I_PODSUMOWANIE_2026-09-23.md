# Podsumowanie kampanii i arena AI

Po ukończeniu treningu albo wczytaniu ukończonej kampanii aplikacja otwiera
podsumowanie zamiast proponować kolejną partię treningową.

## Co pokazuje ekran

- Wynik każdej partii z perspektywy AI, długość, czas decyzji oraz największą
  przewagę materiału AI ze wskazaniem półruchu.
- Pominięte maty w jednym ruchu, sprawdzone przez odtworzenie legalnych ruchów.
  Nie jest to pełna analiza silnikiem. Zmiana materiału po biciu nie jest sama
  w sobie dowodem błędu (może być wymianą lub poświęceniem).
- Powtórki treningu z wyborem partii i suwakiem ruchów.
- Wyniki benchmarku: punkty z pełnych par kolorów, zmiana względem modelu
  sprzed treningu, liczba pełnych par i partie przerwane limitem.
- Osobną tabelę badawczego turnieju każdy z każdym oraz jego podgląd na żywo.

## Drabinka pokazowa

Losowane są cztery miejsca (domyślnie najnowszy model każdej metody).
Przed pierwszym meczem można zmienić AI i checkpoint w każdym miejscu,
limit półruchów oraz tempo oglądania. Każdy półfinał i finał uruchamia się
osobnym przyciskiem Graj. Plansza tekstowa pokazuje ruchy, bilans materiału,
liczbę przeszukanych węzłów i czas decyzji. Można cofać podgląd.

Drabinka jest pokazem, nie zastępuje kontrolowanego benchmarku. Remis albo
limit nie są zamieniane w wygraną: awans jest wówczas jawnie losowany.
Modele są zamrożone, a oryginalny plik kampanii nie jest modyfikowany.

Wyniki, użyte checkpointy, parametry, środowisko i awanse trafiają obok
kampanii do pliku `<nazwa>_arena_<identyfikator>.json`. Można go wczytać
przyciskiem „Wczytaj zapisaną drabinkę” i kontynuować od następnej pary.
Nowe losowanie rozpoczyna osobny zapis, zachowując poprzedni plik.

## Zatrzymanie

„Zatrzymaj mecz” lub Esc zatrzymuje pokaz po zakończeniu bieżącego obliczenia.
Przerwana partia nie przyznaje awansu; ponowne Graj rozpoczyna tę samą parę
od nowa. Zamknięcie okna w czasie obliczenia zgłasza zatrzymanie i czeka na
zakończenie wątku; następnie można zamknąć aplikację. Esc zatrzymuje również
benchmark, a poza obliczeniami zachowuje wyjście z pełnego ekranu.

Benchmark zapisuje ukończone partie. Po zatrzymaniu jego nieukończona partia
jest powtarzana przy wznowieniu. Obserwacja nie dodaje opóźnień do pomiarów
benchmarku; wolniejsze oglądanie dostępne jest w drabince i powtórkach.

## Sprawdzenie

Testy obejmują odtworzenie mata w 1, legalność zapisanych ruchów, zamrożenie
modeli, nienaruszenie kampanii, trzy rundy drabinki, zapis i odczyt, limit
bez fałszywego wyniku oraz Esc w rzeczywistym MainWindow. Dodatkowo są
uruchamiane dotychczasowe testy kampanii, benchmarku i podglądu porównań.
Przebieg regresji: 42 testy zaliczone. Ruff oraz mypy (nowe moduły również
z `--check-untyped-defs`) bez błędów. Układ sprawdzony renderowaniem Qt
w rozdzielczości 1536×864 bez przejmowania myszy użytkownika.

Uruchomienie z katalogu projektu:

```powershell
.\venv\Scripts\python.exe .\scripts\run_gui.py
```

Wczytaj `data/aivsai.sqlite3`. Otwarta wcześniej instancja aplikacji wymaga
ponownego uruchomienia, aby użyć nowego interfejsu.
