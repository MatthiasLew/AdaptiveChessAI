# TODO — stan po domknięciu implementacji

Aktualizacja: 15 września 2026. Wcześniejsze „częściowo” opisywało pierwszy przyrost, ograniczony do dwóch agentów. Poniżej stan obecnego oprogramowania; wykonanie badania z udziałem człowieka jest oddzielnym zadaniem.

| Zadanie | Stan | Co jest dostępne |
|---|---|---|
| Protokół badania | Gotowe | Pytanie, hipoteza robocza, budżety, checkpointy, kryterium przewagi i zasady interpretacji |
| Ocena remisów | Gotowe dla protokołu v2 | Remisy regułowe; limit to `*`, oddzielny licznik, bez sztucznych punktów |
| Trwała pamięć | Gotowe | Profil i wagi, wersje, sumy kontrolne, transakcje SQLite |
| Trening / ocena | Gotowe | Osobne gry kontrolne, zamrożone modele i weryfikacja niezmienności |
| Kampania X partii | Gotowe | Cztery metody, 4X gier, stała kolejność zależna od seeda i zmiana kolorów |
| Autosave i wznowienie | Gotowe | Zapis każdego ruchu, odtworzenie uczenia bez podwojenia aktualizacji |
| GUI gry | Gotowe | Kwadratowe plansze, współrzędne, promocja, poddanie, zakładki i przewijanie |
| Obliczenia w tle | Gotowe | Ruchy w obu trybach gry, osobny proces oceny i turnieju |
| Checkpointy | Gotowe | Stan 0 i po każdej grze wszystkich metod; automatyczna ocena zapisanych stanów |
| Turniej | Gotowe | Cztery metody, obydwa kolory, konfigurowalne otwarcia, domyślnie 36 meczów, wznowienie |
| Agent imitacji | Gotowe | Liniowy ranking ruchów, uczenie z przykładów człowieka, zapis i testy |
| Agent TD | Gotowe | TD(0), perspektywa białych, nagrody terminalne, zapis i testy |
| Statystyki / wykresy | Gotowe | Krzywe, przyrost względem stanu 0, niepewność, kontrola przeciw człowiekowi, CSV/JSON/PGN/PNG |
| Powtarzalność | Gotowe | Seed, limit węzłów, wersje zależności, hash źródeł, manifest paczki, pomiar czasów i aktualizacji |
| Dokumentacja / jakość | Gotowe lokalnie | Instrukcja, protokół, architektura, testy, Ruff, mypy, workflow CI |
| Paczka desktopowa Windows | Gotowe lokalnie | EXE z zależnościami, skrypt budowy i automatyczny test gotowej paczki |
| Pilotaż z użytkownikiem | Do rozegrania | Rzeczywiste gry i ocena wygody obsługi; testy syntetyczne nie zastępują udziału człowieka |
| Badanie do pracy | Do przeprowadzenia | Ustalić plan z promotorem, zebrać partie, wykonać niezależne bloki kontrolne i napisać wnioski |

Dowody i ograniczenia sprawdzeń: [walidacja](WALIDACJA_2026-09-15.md).
Instrukcja rozpoczęcia i interpretacji: [kampania](campaign.md).

Implementacja workflow CI jest gotowa; jego wynik na GitHub będzie znany dopiero po publikacji zmian i wykonaniu workflow. Starsze kampanie v1 i pomocnicze skrypty zachowują dawny protokół; do nowego badania utwórz nową kampanię. Ukończenie oprogramowania nie przesądza, że agent pokona gracza — właśnie to należy zmierzyć.
