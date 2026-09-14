# Kampania: instrukcja i protokół v1

## Pierwsze uruchomienie

1. Uruchom `venv/Scripts/python.exe scripts/run_gui.py` z katalogu repozytorium.
2. W menu wybierz **Kampania badawcza**.
3. Podaj pseudonim, liczbę partii na agenta i głębokość 1 lub 2. Naciśnij **Nowa kampania…** i wskaż nowy plik `.sqlite3`. Istniejące badanie nie zostanie nadpisane.
4. Kliknij **Rozpocznij / wznów partię**. Zagraj z Adaptive, potem z kontrolnym Static. W następnej rundzie zmieniają się kolory człowieka.
5. Po zakończonej partii rozpocznij następną. Możesz poddać partię; zapisuje się to jako porażka człowieka, nie przerwanie ani remis.
6. Aby zrobić przerwę, wróć do menu lub zamknij program po zakończeniu ruchu bota. Każdy ruch jest zapisany automatycznie. W kolejnym uruchomieniu wybierz **Wczytaj kampanię…**, ten sam plik i **Rozpocznij / wznów partię**.
7. Po wykonaniu limitu gier obu agentów wybierz **Uruchom / wznów turniej**.

Parametry widoczne w formularzu służą tworzeniu nowej kampanii. Parametry istniejącego badania są niezmienne. Ruchy bota w kampanii wykonują się w tle. Podczas ruchu wyłączone są działania mogące zmienić sesję. Zamknięcie okna czeka na zakończenie ruchu i zapisu; nie zabija wątku obliczeniowego.

## Co jest badane

AdaptiveMinimax zbiera profil ruchów człowieka: bicia, szachy i wejścia do centrum. Jest to adaptacja heurystyczna. StaticMinimax nie uczy się i jest kontrolą. Oba mają tę samą głębokość, ale ich koszt obliczeń nie jest identyczny.

X oznacza liczbę zakończonych partii na każdego z dwóch agentów, czyli 2X partii człowieka. Poddanie kończy partię i zalicza ją do limitu. Użytkownik nie powinien używać natychmiastowych poddań jako danych badawczych; liczba obserwacji pozwala wykryć pusty trening. Nieukończona partia jest wznawiana i nie zalicza się do X.

Checkpoint 0 przechowuje pusty profil. Każda zakończona partia Adaptive tworzy nowy checkpoint, zachowany razem z numerem gry. Wznowienie aktywnej partii odtwarza jej ruchy na profilu sprzed tej partii. Dzięki temu nie powiela obserwacji. Kampanie różnych uczestników mają oddzielne pliki i stany.

## Turniej

Trzech uczestników: Static, Adaptive-0, Adaptive-final. Każda para gra z obu stron trzech pozycji: startowej, po `e4 e5`, po `d4 d5`. Daje to 18 partii. Wersje botów są zamrożone; po każdym meczu sprawdzana jest niezmienność profilu.

Limit półruchów oznacza maksymalną liczbę ruchów wykonywanych po pozycji startowej danego meczu. Zapisany harmonogram i limit nie zmieniają się przy wznowieniu. Przerwane limitem partie mają wynik `*`, osobny licznik i nie dostają punktów. Raport pokazuje wygrane, remisy, porażki i przerwania; duża liczba przerwań uniemożliwia wiarygodne ustalenie zwycięzcy na podstawie samych punktów.

**Zatrzymaj turniej** kończy proces. Każda ukończona i zapisana partia zostaje w bazie. Po wznowieniu rozgrywana jest ponownie co najwyżej bieżąca niezapisana partia. Zmiana kodu aplikacji, Pythona lub python-chess od początku turnieju blokuje wznowienie, aby nie mieszać warunków oceny.

W tej wersji porównanie odbywa się przed treningiem i po treningu. Automatyczne turnieje checkpointów pośrednich, krzywe uczenia, nowe metody i kontrolne partie przeciw człowiekowi pozostają w planie. Wynik turnieju nie dowodzi przewagi nad człowiekiem.

## Dane i eksport

Plik SQLite jest źródłem prawdy. Zawiera identyfikator kampanii i partii, pseudonim, parametry, początkowy FEN, ruchy UCI, wyniki, powody zakończenia, checkpointy z sumami kontrolnymi, harmonogram i wyniki turnieju. Rejestrowane są wersje Python/python-chess i hash kodu aplikacji. Nie ma losowego agenta w tym protokole, więc seed nie steruje wyborem ruchów.

Obok bazy powstaje katalog `<nazwa>_report`:

- `campaign.json` — pełny eksport kampanii;
- `standings.csv` — tabela turnieju;
- `games.pgn` — zakończone partie treningowe i zapisane mecze turnieju;
- `report.md` — podsumowanie i ograniczenia interpretacji.

Eksport można wykonać przed końcem turnieju; raport będzie częściowy. Pliki raportu są odtwarzalne i nadpisywane przy kolejnym eksporcie. Aktywna partia znajduje się w bazie i JSON, ale nie jest eksportowana jako ukończona partia PGN. Plik kampanii najlepiej przechowywać w `data/campaigns` lub innym własnym katalogu danych. Kopię bezpieczeństwa wykonuj przy zamkniętej aplikacji i zatrzymanym turnieju.

Gra swobodna i stare eksperymenty są niezależne od kampanii. Do badania trwałego uczenia korzystaj z ekranu **Kampania badawcza**.
