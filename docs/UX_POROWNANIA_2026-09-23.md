# Czytelność porównań i podgląd ruchów — 2026-09-23

Zmiany na podstawie testów użytkownika:

- Powrót do menu jest wyróżniony; w porównaniach i raportach znajduje się na górze.
- Dymki pomocy mają opóźnienie 150 ms. Przyciski „? Pomoc” otwierają trwałe okno
  wyjaśnienia, również po aktywacji klawiaturą. Dodano je przy parametrach
  porównań, kampanii, głębokości gry i ustawieniach oraz w raportach.
- Porównanie pokazuje tekstową planszę, ostatni ruch, SAN/UCI i bilans materiału.
  Można wybrać partię, przeglądać ruchy suwakiem/przyciskami i wrócić do trybu
  „Na żywo”. Podgląd zachowuje ostatnie 100 partii bieżącego uruchomienia.
  Bilans materiału nie jest automatycznym rozpoznawaniem błędów szachowych.
- Rzeczywiste wyniki mają osobny wykres z przerwaniami limitem poza remisami.
  Pomocnicza adjudykacja jest opisana oddzielnie. Wykresy mają poziome etykiety,
  całkowite podziałki liczby partii i wartości przy słupkach.
- Podgląd obrazu dopasowuje oba wymiary. „Powiększ wykres” otwiera okno
  z dopasowaniem do dostępnego miejsca oraz trybem 100%.
- Odświeżono 16 wykresów na podstawie istniejących CSV w results/gui_experiments.
  Dane źródłowe i reguły rozgrywania/oceny partii nie zostały zmienione.

Walidacja: pełny przebieg pytest 363/363; po ostatnich poprawkach powiększania
i klasyfikacji wyników dodatkowo 25/25 testów UI oraz 7/7 testów wykresów.
Ruff bez błędów, mypy bez błędów w 133 plikach. Wizualnie sprawdzono motyw
ciemny i jasny, podgląd ruchów, raporty i powiększony wykres. Testy pytest
uruchomiono poza ograniczeniem sandboxa z powodu WinError 5 dla katalogów tmp.

Uruchomienie w PowerShell: `.\venv\Scripts\python.exe scripts/run_gui.py`.
