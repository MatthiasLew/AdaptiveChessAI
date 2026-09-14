# TODO — rozwój AdaptiveChessAI

Stan po pierwszej implementacji kampanii, 14 września 2026.

| Zadanie | Stan | Zakres / co pozostało |
|---|---|---|
| Protokół badania | Częściowo | Jest protokół pilotażowy; ustalić główną hipotezę i pomiar przewagi nad człowiekiem |
| Ocena remisów | Gotowe dla kampanii | Poprawiono automatyczne remisy i brak adaptacyjnej korekty stanów końcowych; starszy format serii nadal ma techniczne remisy |
| Trwała pamięć | Gotowe dla kampanii | Profil, restart, kontrola rewizji i sum kontrolnych |
| Trening / ocena | Gotowe dla kampanii | Turniej nie zmienia agentów; starsze skrypty mają dotychczasową semantykę |
| Kampania X partii | Gotowe, 2 agentów | Adaptive + kontrolny Static, zmiana kolorów, postęp |
| Autosave i wznowienie | Gotowe dla kampanii | Każdy ruch; checkpoint razem z finalizacją gry |
| GUI gry | Częściowo | Duże figury i współrzędne; w kampanii kwadratowa plansza, promocja, poddanie; dalsze testy DPI i ergonomii |
| Obliczenia w tle | Gotowe dla kampanii | Worker ruchów oraz proces turnieju; swobodna gra pozostaje synchroniczna |
| Checkpointy | Gotowe | Po każdej grze Adaptive; automatyczna ocena checkpointów pośrednich do dodania |
| Turniej | Gotowy pilotaż | 18 partii, zmiana kolorów, zamrożone modele, wznowienie; konfigurowalny zestaw otwarć do dodania |
| Agent imitacji | Do zrobienia | Wspólne cechy, trening z przykładów, zapis modelu i testy |
| Agent TD | Do zrobienia | Uczenie wartości pozycji, nagrody i kontrola perspektywy |
| Statystyki / wykresy | Częściowo | Tabela i eksport; krzywe uczenia oraz niepewność do dodania |
| Powtarzalność | Częściowo | Stały protokół, hashe i wersje; pełny manifest środowiska i budżety obliczeń do dodania |
| Pilotaż użytkownika | Do wykonania | Rozegrać rzeczywiste partie w nowej kampanii i ocenić użyteczność |
| Badanie do pracy | Do wykonania | Protokół końcowy, dane, analiza i wnioski |
| Dokumentacja / jakość | Częściowo | README, instrukcja, architektura i testy; CI oraz pakowanie desktopowe pozostają w planie |

Pierwszy przyrost dostarcza pełny przepływ trening → restart → turniej. Nie oznacza ukończenia wszystkich punktów projektu badawczego.

Walidacja tego etapu: **284 testy passed**, Ruff, mypy (110 plików) oraz
`ai-dev check --mode fast --no-cache` przeszły. Test integracyjny GUI wykonuje ruch,
wczytuje kampanię ponownie i uruchamia rzeczywisty proces turnieju 18 partii.
Testy backendu obejmują przerwanie przed odpowiedzią bota, wznowienie turnieju,
niezmienność profilu, konflikt zapisów, uszkodzony checkpoint i eksport PGN.
Render ekranu kampanii obejrzano w Qt offscreen z jawnym ładowaniem fontów systemowych.

Do przygotowania pracy użyto analizatora z checkoutu `freelance-dev-suite`
i narzędzi z checkoutu `ai-dev-cli-tools`. Pierwszy raport intake wykrył pusty
notebook; plik poprawiono. Pełny pytest uruchomiono w środowisku projektu,
poza ograniczeniem sandboxa blokującym katalogi tymczasowe. Nie wykonywano
commitów ani publikacji; zachowano zastaną zmianę testu GUI.
