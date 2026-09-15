# Sprint UX/UI PySide6 — 15.09.2026

## Zakres

Przeprojektowano warstwę prezentacji AdaptiveChessAI. Nie zmieniono plików agentów,
uczenia, protokołu badawczego, generowania wyników, checkpointów ani schematu SQLite.
Zachowano architekturę wielu ekranów, przepływy promocji/poddania, orientację planszy,
podświetlenia i zapis kampanii. Bez commita, pushowania ani publikacji aplikacji.

## Oględziny przed implementacją

Przed edycją uruchomiono aplikację i obejrzano rzeczywiste rendery wszystkich siedmiu
ekranów oraz konfiguracji i gry kampanii. Zrzuty: `.ai/ux/before/`.
Narzędzie pulpitu nie udostępniło okien procesu uruchomionego w środowisku wykonawczym;
obrazy uzyskano przez `QWidget.grab()` działających, pokazanych okien Qt.

| Ekran / obszar | Znaleziony problem |
| --- | --- |
| Menu | Jednakowe przyciski w jednej kolumnie, niejasne „Graj”, dominujące czerwone wyjście. |
| Kampania | Brak grup formularza i aktualnego podsumowania 4X; szerokie pola bez wyjaśnień; ukryte strony narzucały rozmiar aktywnemu widokowi. |
| Gra | Plansza 512×512 pozostawiała pustą przestrzeń; długi panel spychał status i historię pod ekran; FEN konkurował z informacjami o grze. |
| Wyniki | Lista plików na pierwszym planie; brak kart statystyk; techniczne informacje o ścieżkach dominowały nad wynikami. |
| Eksperymenty | Gęsta konfiguracja, długie etykiety, status w formularzu zamiast przy postępie; niewystarczająco opisane porównania. |
| Ustawienia | Jeden formularz mieszał wygląd, grę i foldery; szerokie pionowo ułożone akcje zwiększały przewijanie. |
| Podsumowanie partii | FEN stale widoczny, wielkie przyciski w kolumnie, niezawijany wynik. |
| Motywy / i18n | Light powstawał przez podmianę ciągów dark; części stanów brakowało spójnej palety. Tooltipy i placeholdery nie zmieniały języka. |

## Wdrożony redesign

- **Design system:** osobne słowniki `DARK` i `LIGHT`, jeden generator QSS i natywna
  paleta Qt. Tokeny tła, powierzchni, obramowań, tekstu, akcentu i stanów. Role:
  PrimaryButton, SecondaryButton, DangerButton, Card, SectionCard, PageTitle,
  SectionTitle, HelperText, StatusBadge, StatCard. Stany focus, hover i disabled.
- **Menu:** główna karta kampanii, trzy karty pozostałych obszarów z opisami,
  drugorzędne ustawienia i wyjście; obsługa klawiatury i nazwy dostępności.
- **Kampania:** podstawowy formularz, zwijane zaawansowane ustawienia, opisy czterech
  metod i aktualizowane podsumowanie liczby gier oraz depth/nodes/seed. Dodatkowe
  gry oceny opisano osobno. Rozmiar aktywnej strony nie zależy od ukrytych formularzy.
- **Gra:** centralna, kwadratowa plansza skalowana do przestrzeni; status i agent;
  zakładki ustawień/historii, szczegóły techniczne z FEN. Poddanie i powrót są widoczne.
- **Wyniki:** karty liczby gier i wyników, wykres słupkowy rozkładu, podsumowanie i
  tabela. Raporty/pliki w dolnej zwijanej sekcji. Przerwania pozostają odrębne od
  remisów. Nieudane wczytanie usuwa poprzednie statystyki, aby nie pokazywać starych danych.
- **Eksperymenty:** opis wybranego porównania, zawijane formularze, status przy
  postępie i raporcie, opcjonalny log. Na węższym ekranie kolumny układają się pionowo.
- **Ustawienia:** Wygląd, Gra, Badania / pliki; zwarty wiersz akcji.
- **Pomoc:** znaczenie depth, budżetu węzłów, seed, liczby gier/metodę, checkpointu,
  czterech metod, oceny, turnieju, gry kontrolnej, limitu półruchów, UCI, FEN i plików.
  Tooltipy są zawijane i tłumaczone przez istniejący katalog PL/EN. Pomoc opisuje
  konsekwencje parametru, nie powtarza nazwy przycisku.

## Walidacja

Wynik końcowego pełnego przebiegu: **352 passed, 0 failed**.

`freelance-dev-suite` zakończył sesję `WORK-0001` ze statusem **VERIFIED**.
`ai-dev check --mode full --no-cache`: **3/3 kontrole PASS**, 352/352 testy PASS.
Raporty maszynowe: `.ai/reports/check-full-latest.md` i `.json`;
ślad sesji: `.ai/ux/freelance-verified.log`.

- Ruff: `check src scripts tests` — PASS.
- mypy: PASS, 129 plików źródłowych w konfiguracji projektu.
- `python -m adaptive_chess --smoke` — kod wyjścia 0.
- Macierz wizualna: **24 konfiguracje × 14 widoków = 336 sprawdzeń geometrii**.
  Rozdzielczości 1366×768 i 1920×1080; skale 100%, 125%, 150%; PL/EN; dark/light.
  Dodatkowo zapisano dolne fragmenty przewijanych formularzy. Zrzuty i rozmiary:
  `.ai/ux/matrix/<rozdzielczosc>-<skala>-<motyw>-<jezyk>/`.
- Brak poziomego przewijania zewnętrznych ekranów w całej macierzy. Gra, aktywna
  kampania i jej ocena nie wymagają pionowego przewijania zewnętrznego ekranu.
  Formularze i raporty zachowują przewijanie; ocena ma niezależny scroll obok planszy.
- Skala jest efektywna: skrypt odczytuje bazowe DPI Windows, kompensuje je i sprawdza
  `devicePixelRatio()`. Rozmiar logiczny wynika z fizycznej rozdzielczości i skali,
  z rezerwą na pasek tytułu/zadań. Nie zmieniano ustawień monitora użytkownika.
- Nowe regresje: PL→EN→PL tooltipów/placeholderów bez zmiany danych, aktualizacja
  podsumowania kampanii, zachowanie wyboru metody, klawiatura kart i szczegółów,
  statystyki remisów/przerwań, czyszczenie starych wyników, geometria, podświetlenie
  planszy po zmianie motywu, kontrast tekstu oraz tłumaczenie statusów backendu.
- Istniejący test preferencji zaktualizowano z dawnej etykiety „Graj” i koloru
  wpisanego na sztywno na nazwę karty i token LIGHT. Nie usunięto testów.

### Odtworzenie kontroli wizualnej

```powershell
.\venv\Scripts\python.exe scripts\gui_visual_smoke.py --width 1366 --height 768 --scale 1.5 --theme light --language en --output .ai/ux/review
```

Skrypt tworzy własne dane demonstracyjne w katalogu tymczasowym. Nie otwiera ani
nie nadpisuje zapisów użytkownika. Tabele na zrzutach to dane demonstracyjne.

### Narzędzia lokalne

Użyto `C:\Users\Praca\fork\MatthiasLew\freelance-dev-suite` i
`C:\Users\Praca\fork\MatthiasLew\ai-dev-cli-tools`. Sesja `WORK-0001` i jej ślad
znajdują się w `.ai/ux/freelance/`. Początkowa autodetekcja ai-dev wybrała interpreter
narzędzia, ponieważ rozpoznaje `.venv`, a aplikacja używa `venv`. Końcowe sprawdzenie
korzysta z jawnych poleceń zapisanych w `.ai/ux/validation.toml`; tymczasowy plik
konfiguracji w korzeniu jest usuwany po zakończeniu. Brak danych telemetrycznych
pozostaje zerem/niezmierzonym zużyciem, nie deklaracją oszczędności.

Testy wymagające własnych katalogów tymczasowych uruchomiono poza sandboxem po
potwierdzeniu błędów uprawnień Windows. Nie zmieniano kodu aplikacji w celu omijania
tych błędów. Końcowy pełny przebieg odbył się bez równoległych zmian źródeł.

## Zmienione i nowe pliki

| Plik | Zmiana |
| --- | --- |
| `src/adaptive_chess/ui/theme.py` | Palety, generator QSS, natywna paleta. |
| `src/adaptive_chess/ui/help_text.py` | Nowy katalog pomocy kontekstowej. |
| `src/adaptive_chess/ui/i18n.py` | Nowe teksty, tooltipy, placeholdery, dostępność, statusy. |
| `src/adaptive_chess/ui/main_window.py` | Paleta i bezpieczny rozmiar początkowy dla DPI. |
| `src/adaptive_chess/ui/widgets/components.py` | Nowe wspólne komponenty i układy. |
| `src/adaptive_chess/ui/widgets/chess_board_widget.py` | Skalowanie figur i mniejszy minimalny rozmiar pól. |
| `src/adaptive_chess/ui/screens/menu_screen.py` | Karty nawigacji. |
| `src/adaptive_chess/ui/screens/campaign_screen.py` | Formularz, pomoc, podsumowanie i układ gry/oceny. |
| `src/adaptive_chess/ui/screens/game_screen.py` | Plansza, status, zakładki i szczegóły. |
| `src/adaptive_chess/ui/screens/game_summary_screen.py` | Hierarchia, zawijanie, szczegóły FEN, akcje. |
| `src/adaptive_chess/ui/screens/results_screen.py` | Karty, rozkład wyników, dolna sekcja plików. |
| `src/adaptive_chess/ui/results_presenter.py` | Wspólny odczyt danych dla dotychczasowego podsumowania i kart. |
| `src/adaptive_chess/ui/screens/experiments_screen.py` | Konfiguracja, opisy, postęp i układ responsywny. |
| `src/adaptive_chess/ui/screens/settings_screen.py` | Trzy sekcje ustawień. |
| `tests/integration/test_ui_polish.py` | 15 nowych przypadków regresyjnych po parametryzacji. |
| `tests/integration/test_preferences_and_reports.py` | Asercje nowej nawigacji i tokenów. |
| `scripts/gui_visual_smoke.py` | Powtarzalna macierz renderowania i kontroli wymiarów. |
| `docs/UX_UI_POLISH.md` | Ten raport. |

## Granice i pozostałe ograniczenia

- Istniejący `environment_compatible()` uwzględnia hash wszystkich plików Python,
  także UI, oraz już istniejącą listę dopuszczonych wersji. Nie rozszerzano jej.
  Kampanie z innych hashy mogą wymagać pierwotnej wersji aplikacji. Nie wykonano
  migracji ani zmian manifestów. Testy sprawdzają nowe kampanie i ich wznowienie.
- Nie zmieniano statystycznej interpretacji wyników ani zawartości eksportów.
  Zestawienie folderu zachowuje istniejące reguły wyboru źródeł danych; duże raporty
  nadal pokazują do 200 wierszy, z pełnymi danymi dostępnymi w plikach.
- Kontrola wizualna obejmuje rzeczywiste rendery Qt, nie ręczne testy na trzech
  fizycznie przełączanych konfiguracjach monitora. Przejrzano wszystkie typy ekranów
  oraz reprezentatywne stany w obu motywach/językach; cała macierz ma automatyczne
  sprawdzenie geometrii. Nie jest to pełny audyt czytników ekranu.


## Korekta po uwagach użytkownika i zrzutach ekranu

### Znalezione problemy

- Menu rozciągało karty na całą szerokość dużego monitora i pozostawiało
  nieproporcjonalnie dużo pustej przestrzeni.
- Spinbox głębokości miał zakres 1–4, ale nie tłumaczył skali ani tego,
  że RandomBot nie korzysta z przeszukiwania.
- Tooltipy eksperymentów były mało odkrywalne.
- Podsumowanie usuwało planszę z widoku dokładnie w momencie zakończenia gry.

### Poprawki

- Menu ma wyśrodkowaną treść o maksymalnej szerokości 1060 logicznych pikseli.
  Karty pozostałych akcji mieszczą się w rzędzie także przy 1366×768 / 150%.
- Ustawienia mają zamknięty wybór: 1 — Szybkie, 2 — Umiarkowane,
  3 — Dokładne, 4 — Najgłębsze. Opis wyjaśnia półruchy, czas obliczeń i brak
  gwarancji siły Elo. Dla RandomBot pole jest nieaktywne, z wyjaśnieniem dlaczego.
  Zapis nadal używa tego samego pola `default_depth` i wartości 1–4.
- Eksperymenty: przyciski `?`, tooltipy pól i etykiet; pomoc można otworzyć
  klawiszem Spacja. Wszystkie nowe teksty działają w PL/EN.
- Podsumowanie: cała końcowa plansza obok wyniku, zachowana orientacja i ostatni
  ruch. Szachowany król jest zaznaczony. Objaśnienia mata i pata wynikają z
  legalności zapisanej pozycji; zakończenia z innych powodów nie są nazywane matem.
  Historia oraz szczegóły zajmują osobne zakładki. Plansza służy do oglądania;
  kliknięcia nie zmieniają pozycji ani wyników.
- API `ChessBoardWidget.set_board()` przyjmuje opcjonalny argument nazwany
  `last_move`, potrzebny dla eksportowanego FEN bez stosu ruchów. Dotychczasowe
  wywołania zachowują działanie. Backend, protokół i formaty danych bez zmian.

### Zmienione pliki w tej korekcie

`ui/screens/menu_screen.py`, `ui/screens/settings_screen.py`,
`ui/screens/experiments_screen.py`, `ui/screens/game_summary_screen.py`,
`ui/widgets/chess_board_widget.py`, `ui/widgets/components.py`, `ui/i18n.py`
(wszystkie pod `src/adaptive_chess/`), `tests/integration/test_ui_polish.py`,
`scripts/gui_visual_smoke.py` oraz ten raport.

### Walidacja korekty

- 24 konfiguracje: 1366×768 i 1920×1080, skale 100/125/150%, dark/light, PL/EN.
- 360 renderów Qt, w tym rzeczywista pozycja mata po legalnej sekwencji ruchów.
  Brak poziomego przewijania; cała plansza mata mieści się bez przewijania pionowego.
- Dowody: `.ai/ux/followup/matrix/*/geometry.json` i pliki PNG obok.
- Smoke: `PYTHONPATH=src venv/Scripts/python.exe -m adaptive_chess --smoke`: kod 0.
- Sesja lokalnego freelance-dev-suite: `WORK-0002`; pełne sprawdzenie przez
  lokalne ai-dev-cli-tools (wynik końcowy poniżej).

- Wynik końcowy: **358/358 pytest PASS**, Ruff PASS, mypy PASS (129 plików).
  Dodano 6 przypadków regresji: mate/pat/inny powód zakończenia, zapis poziomów,
  wyświetlanie ostatniego ruchu z FEN oraz pomoc z klawiatury z tłumaczeniem.
- `WORK-0002`: **VERIFIED**, 3/3 pełne kontrole PASS. Raport narzędzia:
  `.ai/reports/check-full-latest.md` i `.json`. Tymczasową konfigurację poleceń
  usunięto po walidacji. Nie publikowano ani nie commitowano zmian.
