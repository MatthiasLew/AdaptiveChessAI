# Brak odświeżenia po macie w kampanii

Zgłoszenie: po 72 półruchach ekran pozostawał przy `36...Kd5`, a kolejne
kliknięcia wyświetlały „Nielegalny ruch”. Odtworzona pozycja:
`8/8/8/3k4/8/1P2Q1PB/1B2K3/2R4R w - - 3 37`.

W bazie `data/1.sqlite3` był już zapisany 73. półruch `h1d1` (`Rhd1#`).
W `data/2.sqlite3` również istniała aktywna, zamatowana partia (93 półruchy).
Obie bazy miały zero zakończonych partii i zachowaną pełną historię ruchów.

Przyczyna: zmiany plików podczas testowania interfejsu zmieniły hash źródeł.
`ResearchCampaign.finish()` ponownie wywoływał `resume()`, którego kontrola
środowiska zgłaszała `ValueError` także dla istniejącej sesji. Finalizacja
odbywała się w slocie GUI, który tego wyjątku nie obsługiwał. Plansza pokazywała
stan sprzed mata, a sesja już po macie miała turę czarnych i zero legalnych ruchów.

Naprawa:

- Istniejąca sesja może dokończyć zapis swoim załadowanym agentem; nowe sesje
  i rekonstrukcja zapisów nadal podlegają kontroli środowiska.
- Dodano zgodność dokładnie trzech znanych wersji zmian GUI z tej sesji prac.
  Kod agentów i reguły treningu w tych wersjach nie zmieniły się. Oryginalne
  manifesty kampanii pozostają zachowane; nieznane wersje nadal są odrzucane.
- Finalizacja odbywa się w workerze. Błędy trafiają do obsługi GUI, która pokazuje
  aktualną planszę i wymaga wczytania zapisu, zamiast pozostawiać mylący ekran.
- Ekran nie pozwala wybierać ruchów w zakończonej partii ani podczas tury bota.

Walidacja: 24/24 testy regresji kampanii i GUI, Ruff bez błędów, mypy bez błędów
w 134 plikach. Na kopiach SQLite potwierdzono odzyskanie obu zwycięstw 1–0,
zachowanie ruchów i manifestów oraz brak zmian w oryginałach. Kopie weryfikacyjne:
`.ai/mate-recovery-20260923/`. Powtórne wczytanie zakończonej kampanii nie dubluje
wyniku ani checkpointu.

Kontynuacja: ponownie uruchomić aplikację i wczytać oryginalną kampanię.
Przywrócenie terminalnej aktywnej pozycji zapisze wynik i pokaże zwycięstwo.

## Czytelne wczytywanie po błędzie

Po kolejnym zgłoszeniu dodano stały nagłówek z przyciskami „Wczytaj kampanię…”
i „Powrót do menu” oraz pełną, kopiowalną ścieżką zapisu. Okno wyboru zaczyna
w folderze ostatniej kampanii, a przy pierwszym użyciu w `data`.

Błąd prowadzi do osobnego ekranu bez planszy i akcji gry. Dostępne są
„Wczytaj ponownie tę kampanię” (bez ponownego szukania pliku) i „Wybierz inny
zapis…”. Surowy wyjątek jest pod „Szczegóły błędu”. Niezgodność wersji jest
wyjaśniona osobno — samo ponowienie nie jest przedstawiane jako jej rozwiązanie.
Odtwarzanie zapisanej partii ma własny komunikat oczekiwania. Wczytany aktywny
zapis pokazuje swoją pozycję i „Wznów zapisaną partię”, zamiast planszy startowej.

Testy obejmują kliknięcie ponownego wczytania, odzyskanie mata, niezgodność wersji,
brak pliku i wybranie innego zapisu. Wizualnie sprawdzono ekran odzyskiwania.
