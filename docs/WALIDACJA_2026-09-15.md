# Walidacja domknięcia implementacji — 15 września 2026

## Wynik

Dodano dwie metody uczące (imitacja i TD), czterometodową kampanię, ocenę wszystkich checkpointów, niezależne partie kontrolne przeciw człowiekowi, krzywe z niepewnością, pomiar kosztów, manifest środowiska, obliczenia swobodnej gry w tle, paczkę Windows oraz workflow CI.

## Wykonane sprawdzenia

- Pełny pytest: **300 passed**, 18.64 s, Windows / Python 3.13.15 / Qt offscreen. Uruchomienie poza sandboxem, ponieważ jego ograniczenia blokują katalogi tymczasowe pytest.
- Ruff: cały `src`, `scripts`, `tests`.
- Mypy: **118 plików**, bez błędów.
- `ai-dev check --mode fast --no-cache`: lint i typecheck. Ten tryb nie uruchamia pytest; pełne testy wykonano osobno w venv projektu.
- `freelance-dev-suite`: analiza wejściowa projektu zapisana lokalnie w `.ai/reports/completion-intake.json`; jej brak CI odnosił się do stanu sprzed dodania workflow.
- Integracja GUI: ruch w workerze, ponowne wczytanie, rzeczywisty proces starego turnieju oraz proces oceny czterech metod (16 meczów checkpointów i 12 turnieju przy jednym otwarciu).
- Backend: reprodukowalne legalne ruchy z limitem węzłów, uczenie imitacji wyłącznie z ruchów człowieka, kierunek nagrody TD i pojedyncza aktualizacja terminalna, niezmienność oceny, wznowienie po awarii, kontrola środowiska, model po restarcie, eksporty oraz brak pozornej pewności przy małej próbce kontrolnej.
- Obejrzano render GUI przy 1366×768 oraz skalowaniu 150%. W mniejszym logicznym obszarze dostęp zapewniają paski przewijania. Render offscreen wymagał jawnego załadowania lokalnych fontów Segoe UI/Symbol. Nie jest to test na fizycznym monitorze innego komputera.
- PyInstaller: zbudowana paczka Windows. Test gotowego EXE wykonany poza repozytorium: start GUI, stary skrypt, ocena checkpointów, turniej, ponowne wznowienie, niezmienność modeli i eksporty CSV/JSON/PGN/PNG.

## Wykryte i usunięte problemy

Pierwszy build był niekompletny mimo kodu wyjścia 0. `collect_submodules` nie widział pakietu przed ustawieniem ścieżki importów; builder teraz przekazuje PYTHONPATH. Drugi problem to biblioteka `icuuc.dll` pobrana przez PyInstaller z Popplera obecnego w PATH. Eksportowała symbole ICU z innym sufiksem niż oczekiwało Qt. Builder ogranicza PATH do Pythona i Windows; gotowy EXE po tej poprawce uruchamia GUI.

Dodatkowo test sprzątania po pracy paczki ujawnił, że sam kontekst transakcji SQLite nie zamyka połączenia. Dodano jawne zamykanie wszystkich trzech ścieżek dostępu do bazy oraz test, który utrzymuje referencje do połączeń i sprawdza ich zamknięcie bez polegania na garbage collectorze.

## Granice dowodów

Partie testowe są syntetyczne, z małymi limitami i poddaniami. Sprawdzają program, nie skuteczność agentów. Nie zebrano w tej zmianie rzeczywistych danych użytkownika i nie ustalono naukowo przewagi nad człowiekiem. Próg w raporcie jest operacyjny i wymaga planu badania oraz niezależnego potwierdzenia.

Workflow zapisano, ale nie wykonano go jeszcze zdalnie. Nie potwierdzono uruchomienia na drugim komputerze, Linux ani macOS; lokalny artefakt to Windows x64. Nie wykonano w tym etapie nowego commita ani push. Zachowano wcześniejsze zmiany wcięć użytkownika w teście GUI; dodano obsługę oczekiwania na ruch w tle oraz test braku blokowania GUI i ochrony zamknięcia okna.

## Uzupełnienie testów na prośbę użytkownika

Po poprzedniej walidacji dodano 23 przypadki regresyjne i uporządkowano testy nowych funkcji według warstw. Szczegóły: [mapa testów](../tests/README.md). Pełny wynik: **323 passed, 15.26 s**. Uzupełnienia obejmują nieprawidłowy protokół, uszkodzenie checkpointu, balans kolorów po restarcie, izolację gier kontrolnych, wybór mata, nieprawidłowe wagi, nagrodę remisową TD i interpretację wyników. Eksport PGN jest ponownie parsowany, sprawdzany pod kątem legalności ruchów i zgodności końcowego FEN z zapisem.

Ruff/mypy przez `ai-dev check --mode fast --no-cache` zakończyły się sukcesem. Użyto również analizatora `freelance-dev-suite`; lokalny wynik znajduje się w `.ai/reports/test-followup-intake.json`. To uzupełnienie zmienia testy i ich dokumentację, bez zmian kodu aplikacji.

## Poprawki UX po rzeczywistej partii użytkownika

Przebieg zmieniono na **Graj → Nowa / Wczytaj kampanię → Plansza**. Parametry tworzenia kampanii znajdują się przed grą. Podczas gry są osobne zakładki ruchów oraz oceny/raportu. Po ruchu człowieka GUI pokazuje jego pozycję, czeka 850 ms bez blokowania wątku GUI, a następnie uruchamia odpowiedź bota. Ostatni ruch ma wyróżnione oba pola i komunikat z SAN oraz polem początku/końca. Pauza jest poza pomiarem czasu wyboru ruchu.

Po końcu partii zachowywane są finalna plansza i wynik z perspektywy człowieka. Kolejna partia wymaga jawnego kliknięcia. Poprzedni kod resetował widok planszy po finalizacji, co wyglądało jak rozpoczęcie kolejnej gry. Wynik jest teraz widoczny również po ponownym wczytaniu kampanii.

Pełna regresja: **329 passed, 29.15 s**. Nowe przypadki obejmują wybór kampanii, fazę oczekiwania na bota, podświetlenie jego ruchu, mat/pat, zachowanie wyniku i planszy oraz zgodność zapisów znanej poprzedniej paczki. Obejrzano rendery nowych ekranów przy 1180×760. Ruff/mypy przeszły; `ai-dev-cli-tools` oraz `freelance-dev-suite` zostały użyte ponownie (lokalne raporty `.ai/reports/ui-flow-quality.txt` i `ui-flow-intake.json`).

Paczka `dist/AdaptiveChessAI/AdaptiveChessAI.exe` została przebudowana. Test gotowego programu poza repozytorium przeszedł: GUI, CLI, ocena, turniej, wznowienie i eksporty. Oryginalny manifest poprzedniej zgodnej kampanii jest zachowany, a nowe partie zawierają dodatkowy manifest uruchomienia. Zgodność dotyczy konkretnej zweryfikowanej poprzedniej wersji i nie pomija kontroli pozostałych wersji zależności.

## Pełny ekran, preferencje i czytelne raporty

Aplikacja domyślnie startuje w pełnym ekranie. F11 przełącza tryb, Esc wraca do zmaksymalizowanego okna. Ustawienia zapisują język interfejsu PL/EN, motyw jasny/ciemny, tryb startu oraz opóźnienie odpowiedzi bota 300–3000 ms. Zmiana wyglądu nie odtwarza kampanii. Tłumaczenia obejmują etykiety interfejsu; istniejące raporty, logi i część dynamicznych komunikatów zachowują język źródłowy.

Wyniki przedstawiają podsumowania i tabele partii oraz podgląd wykresów. Pliki techniczne są domyślnie ukryte. Partie zatrzymane limitem są wyraźnie oddzielone od remisów. Markdown jest renderowany, a zbiorczy raport zestawu eksperymentów korzysta z czytelnego podsumowania CSV.

Eksperymenty otrzymały opisy porównań, objaśnienia parametrów, wskaźnik pracy i podsumowanie wyników. Log techniczny jest opcjonalny. Naprawiono import pakietu w pełnym zestawie eksperymentów oraz kodowanie wyjścia procesów, także w EXE (samo PYTHONIOENCODING nie wystarczało w spakowanym interpreterze). Wykresy procesów eksperymentalnych korzystają z backendu Agg.

Walidacja: pełny zestaw **337 passed (160.28 s)**. Po ostatnich poprawkach wejścia EXE i tłumaczeń: **74 passed (27.91 s)** w testach preferencji/raportów, kampanii GUI i jednostkowych UI. Końcowy Ruff przeszedł; mypy sprawdził 125 plików bez błędów. Obejrzano rendery wyników, jasnego motywu i angielskich etykiet. To render offscreen, nie test na drugim fizycznym komputerze.

Użyto obu wskazanych narzędzi: ai-dev-cli-tools (kontrole jakości) i freelance-dev-suite (analiza projektu). Lokalne raporty: `.ai/reports/preferences-quality.txt` oraz `.ai/reports/preferences-intake.json`. Tryb fast nie zastępuje osobno wykonanych testów pytest.

Końcowa paczka EXE została przebudowana i przeszła rozszerzony test poza repozytorium: GUI, starszy skrypt, pełny zestaw eksperymentów, ocena, turniej, wznowienie, niezmienność modeli i eksporty. Wyjście procesów dekodowano jako ścisłe UTF-8. Manifest paczki jest zgodny z końcowymi źródłami i zależnościami. Dowód: `.ai/reports/preferences-desktop-smoke.log`; build: `.ai/reports/preferences-build-final.log`. W tym etapie nie wykonano commita ani push.
