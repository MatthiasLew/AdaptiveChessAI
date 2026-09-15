# Kampania badawcza — protokół v2

## Przebieg w aplikacji

1. Uruchom `venv/Scripts/python.exe scripts/run_gui.py` albo rozpakowane `AdaptiveChessAI.exe`.
2. Wybierz **Graj → Nowa kampania**. Aby wrócić do zapisu, wybierz **Graj → Wczytaj kampanię…**. Podaj pseudonim, X partii na metodę, głębokość, limit węzłów i seed. Otwarcia to ruchy UCI oddzielone spacjami, a zestawy oddziela średnik; pusty zestaw oznacza pozycję początkową.
3. Kliknij **Utwórz kampanię i graj…** i zapisz nowy plik `.sqlite3`. Pierwsza partia rozpocznie się po utworzeniu kampanii. Parametry utrwalonego badania są stałe. Zmiany w formularzu służą następnej kampanii.
4. Po zakończeniu gry ekran pokazuje **Wygraną / Przegraną / Remis**, wynik i końcową pozycję. **Rozpocznij następną partię** przechodzi dalej dopiero po Twoim kliknięciu. Kolejność ustala seed; w każdej rundzie człowiek gra po jednej partii z każdą metodą. Kolory zmieniają się co rundę. X oznacza **4X partii człowieka**.
5. Kliknij figurę i pole docelowe. Przy promocji wybierz figurę. Poddanie oznacza porażkę, a nie remis. Każdy ruch zapisuje się automatycznie. Po restarcie wczytaj plik i wznów grę.
6. W zakładce **Ocena i raport** ustaw limit półruchów, zanim po raz pierwszy uruchomisz **Oceń checkpointy / turniej**. Aplikacja automatycznie oceni wszystkie zapisane checkpointy, także checkpoint 0. Po ukończeniu treningu rozegra również turniej końcowy. Można oceniać przed zakończeniem treningu, a później dołączyć nowe checkpointy. Przycisk zatrzymania zachowuje ukończone mecze; wznowienie powtarza najwyżej bieżący niezapisany mecz.
7. Aby sprawdzić przewagę nad sobą, wybierz metodę i numer checkpointu w zakładce **Ocena i raport**, a następnie **Partia kontrolna (bez nauki)**. Te partie mają oddzielny zbiór danych. Kolejne partie danego checkpointu zmieniają kolor człowieka. Przerwaną grę wznawia zwykły przycisk wznowienia.
8. **Eksportuj raport i partie** otwiera raport z wykresem. Pliki powstają obok bazy w `<nazwa>_report`.

Obliczenia nie blokują wątku GUI. Podczas ruchu działania zmieniające sesję są wyłączone. Zamknięcie okna wymaga zakończenia bieżącego ruchu i zapisu. Mniejszy budżet węzłów skraca oczekiwanie. Oba tryby gry mają kwadratową planszę, promocję i poddanie; przewijanie udostępnia kontrolki przy małym oknie lub dużym skalowaniu ekranu.

## Metody i kontrola

| Metoda | Co się uczy | Źródło informacji |
|---|---|---|
| adaptive | Profil częstości bić, szachów i gry w centrum | Ruchy człowieka |
| imitation | Liniowy ranking ruchów, gradient log-likelihood softmax | Legalne alternatywy oraz ruch wybrany przez człowieka |
| td | Liniowa funkcja wartości z tanh, aktualizacja TD(0) | Przejścia obu stron i wynik końcowy |
| static | Nic; kontrola | Stała ocena materialna i pozycyjna |

Wszystkie metody korzystają z tego samego wyszukiwania alfa-beta, głębokości i maksymalnego budżetu odwiedzonych węzłów. Budżet jest górnym limitem, nie gwarancją jednakowego czasu: funkcje cech mają różny koszt. Gdy budżet jest bardzo mały, przeszukiwana jest tylko część ruchów. Seed ustala deterministyczną kolejność ruchów w korzeniu, także przy remisach oceny.

Imitacja wykorzystuje 11 cech: bicie, szach, centrum, roszada, promocja i rodzaj figury. Uczy preferencji zaobserwowanego gracza, co samo w sobie nie gwarantuje pokonania go. TD używa 7 cech pozycji: różnic liczby figur, kontroli centrum i strony na ruchu. Wartość i nagrody mają konsekwentnie perspektywę białych: +1 wygrana białych, -1 czarnych, 0 remis. Aktualizacja to `w += alpha * (target - tanh(w·phi)) * (1-tanh(w·phi)^2) * phi`. Dla przejścia niekońcowego target to `gamma * V(next)`, a dla końcowego nagroda. Poddanie aktualizuje ostatnią pozycję raz. Domyślnie alpha=0.05, gamma=0.99; zapis zawiera te parametry. Wyszukiwanie TD dodaje `3*V` do wspólnej oceny pozycji.

Są to niewielkie modele liniowe i adaptacja heurystyczna. Nie są sieciami neuronowymi ani odtworzeniem AlphaZero. Startują ze wspólną wiedzą szachową zakodowaną w ocenie pozycji; badanie mierzy dodatkowy efekt uczenia. TD początkowo dostaje sygnał dopiero z rozstrzygnięcia, dlatego pierwsze gry mogą dawać niewielką zmianę. Implementacja nie obiecuje, że którykolwiek agent osiągnie przewagę.

Podstawa metod: [Sutton i Barto, rozdział 6 o TD](https://www.andrew.cmu.edu/course/10-703/textbook/BartoSutton.pdf); problem uczenia z demonstracji i rozkładu stanów omawiają [Ross, Gordon i Bagnell](https://proceedings.mlr.press/v15/ross11a.html). Implementacja imitacji nie jest algorytmem DAgger.

## Pytanie badawcze i pomiar

Pytanie: jak liczba partii z konkretnym graczem nieeksperckim wpływa na skuteczność poszczególnych metod przy tym samym limicie wyszukiwania? Hipoteza robocza: co najmniej jedna metoda ucząca poprawia wynik względem własnego checkpointu 0 oraz kontroli statycznej. Nie utożsamiaj zwycięzcy turnieju z udowodnioną przewagą nad człowiekiem.

Przed zbieraniem danych ustal X, uczestników, kryterium nieeksperckości (np. deklarowany ranking i doświadczenie), sprzęt, otwarcia, budżety, główny checkpoint i harmonogram bloków kontrolnych. Nie wybieraj korzystnego limitu lub metody po zobaczeniu wyników. Pilot służy sprawdzeniu czasu i ergonomii; właściwe badanie zaczyna się od nowych pustych kampanii. Jeden plik przypada na uczestnika; ten sam seed ułatwia odtwarzanie, różne wcześniej ustalone seedy między uczestnikami ograniczają efekt kolejności.

Checkpoint powstaje po każdej partii każdego agenta. Ocena checkpointu obejmuje zamrożonego agenta przeciw static-0 z oboma kolorami dla każdego otwarcia. Dla O otwarć i X ukończonych gier każdego agenta daje to `4*(X+1)*2*O` meczów. Turniej końcowy to `6*2*O`, domyślnie **36 meczów**. Trzy domyślne otwarcia służą pilotowi; dla badania trzeba z góry wybrać większy, zróżnicowany zestaw. Kopie identycznych sekwencji otwarcia są odrzucane.

Wygrana=1, remis=0.5, porażka=0. Limit półruchów daje `*`, nie remis. Krzywe używają wyłącznie pełnych par kolorów i pokazują licznik przerwań. Masowe przerwania ograniczają interpretację i mogą prowadzić do selekcji wyników; nie ukrywaj ich. Bootstrap 2000 próbek par otwarć daje opisowy przedział 95% dla danego zestawu pozycji, nie dla populacji graczy.

Operacyjny próg przewagi nad człowiekiem: co najmniej 10 zakończonych gier kontrolnych w pełnych parach kolorów, wynik agenta >=60% i dolna granica 95% >50%. Granica Hoeffdinga jest liczona dla średnich par: `mean +/- sqrt(log(40)/(2*n_pairs))`, ograniczona do [0,1]. Nie zeruje niepewności po samych zwycięstwach. W praktyce 10 partii może nie wystarczyć do spełnienia progu. Partie kontrolne nie zmieniają modelu i nie wchodzą do X. Gracz nadal może uczyć się podczas badania, więc założenie niezależności par jest ograniczeniem.

Pierwszy checkpoint spełniający próg jest wynikiem eksploracyjnym. Potwierdź go nowym blokiem z góry ustalonej długości, bez kolejnego wybierania punktu zatrzymania. Przy porównywaniu wielu metod/checkpointów nie traktuj pojedynczego przedziału 95% jako skorygowanego testu wielokrotnego. W pracy podaj wszystkie wyniki, wielkości prób, ograniczenia i przypadki bez osiągnięcia progu. Brak przewagi jest dopuszczalnym wynikiem badania.

## Dane, koszty i wznowienie

SQLite zawiera protokół, seed, pseudonim, czasy UTC, stany modeli, checkpointy SHA256, aktywną historię, wyniki i harmonogramy. Wersje Pythona, chess, PySide6, pandas, matplotlib, platforma i hash źródeł opisują środowisko. Wersja desktopowa zawiera manifest źródeł z momentu budowy. Zmiana środowiska blokuje kontynuację nowego badania; zachowaj używaną aplikację wraz z bazą.

Ruchy są zapisywane transakcyjnie z kontrolą rewizji. Restart odtwarza uczenie z modelu sprzed gry i jej ruchów, bez ponownego naliczania zapisanych metryk. Model po grze i zakończenie gry zatwierdzane są razem. Ocena ładuje osobne zamrożone kopie i sprawdza ich niezmienność.

Eksport:

- `campaign.json`: pełny zapis, również aktywna gra i manifest;
- `learning.csv`: wynik każdego checkpointu, przyrost względem 0, pary, przedziały, przerwania, aktualizacje, węzły i czasy obliczeń;
- `human_evaluation.csv`: kontrolne wyniki przeciw człowiekowi i próg;
- `standings.csv`: W/D/L, punkty i przerwania turnieju;
- `learning.png`, `report.md`: wykres i opis;
- `games.pgn`: ukończone gry treningowe, kontrolne i wszystkie zapisane mecze automatycznej oceny.

`decision_seconds` mierzy wybór ruchów, `learning_seconds` aktualizacje modeli. Liczba ruchów i partii jest podstawowym kosztem próbek. Różnica UTC początku i końca partii obejmuje również myślenie człowieka i przerwy; nie myl jej z czasem uczenia procesora. Czasów nie można oczekiwać identycznych między uruchomieniami. Kopię SQLite wykonuj przy zamkniętej aplikacji.

Stare kampanie dwóch agentów nadal działają według v1 (18 meczów). Nie mieszają się automatycznie z nowym protokołem czterech metod. Gra swobodna i starsze skrypty są trybami pomocniczymi, nie źródłem danych tej kampanii.

## Czytelność ruchów i zgodność zapisu

Po ruchu człowieka plansza pokazuje jego nową pozycję. Odpowiedź bota zaczyna się po pauzie 850 ms; pauza nie jest wliczana w czas wyboru ruchu agenta. Ostatni ruch ma podświetlone pole początkowe i końcowe, a komunikat podaje np. `Bot: Nf6 (g8 → f6). Twój ruch.` Pauza nie blokuje obsługi GUI.

Aktualizacja interfejsu zachowuje zgodność z poprzednią zweryfikowaną paczką z 15 września (hash źródeł `3ec6a4a0990fc51d9d90eb12cfa543a2259b0c679011bf0cb8e3774217dd3d5c`), jeżeli pozostałe warunki środowiska są identyczne. Oryginalny manifest pozostaje w bazie; nowe partie zapisują dodatkowo manifest bieżącego uruchomienia. Nie zmieniono metod uczenia ani budżetów. Nieznane wersje źródeł nadal nie mogą kontynuować badania automatycznie.
