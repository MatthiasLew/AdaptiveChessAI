> Dokument historyczny: diagnoza sprzed implementacji. Aktualny stan: [TODO](TODO.md), [protokół v2](campaign.md) i [walidacja](WALIDACJA_2026-09-15.md).

# AdaptiveChessAI — audyt i propozycja rozwoju

Data: 14 września 2026. Analizowany lokalny HEAD: `920d1f20786d68dd5d19dbe675bf47bca78cbb1c`.

## 1. Wniosek

Projekt ma użyteczny fundament: reguły szachowe, sesję człowiek–bot, GUI PySide6, minimax, profil przeciwnika, serie rozgrywek, eksport oraz analizę wyników. Brakuje jednak warstwy, która łączy te elementy w zamierzony eksperyment: **człowiek rozgrywa X partii z każdym agentem, agenci zachowują zdobyte doświadczenie, a ich zapisane wersje uczestniczą w ocenie i turnieju**.

Obecna aplikacja jest zestawem narzędzi do gry i eksperymentów. Docelowo powinna prowadzić użytkownika przez jedną kampanię badawczą. Samo dodanie mocniejszego silnika albo poprawienie wyglądu nie rozwiąże braku ciągłości treningu i pomiaru.

Nie proponuję przepisywania projektu od zera. Proponuję zachować Python, PySide6, python-chess i znaczną część obecnych modułów, a dodać trwały model kampanii, interfejs uczącego się agenta oraz kontrolowany protokół oceny.

## 2. Zakres i dowody

Przegląd objął wszystkie obszary repozytorium: logikę gry, boty, adaptację, wyszukiwanie, ocenę pozycji, eksperymenty, sesję człowieka, eksport, statystykę, skrypty, ekrany GUI, testy, dokumentację, zależności i konfigurację dostarczania aplikacji. Szczegółowo prześledzono krytyczne ścieżki danych i ich testy; nie jest to formalny dowód poprawności każdej funkcji ani pełny audyt podatności zależności.

Repozytorium ma 117 śledzonych plików; narzędzie freelance wykazało 104 pliki źródłowe i 9293 niepuste linie kodu, wliczając testy i skrypty. Zastana lokalna zmiana w `tests/integration/test_gui_smoke.py` dotyczy wcięć i została zachowana. Nie zmieniono kodu aplikacji ani istniejących testów. Nie wykonano commita ani publikacji.

Użyte narzędzia z podanych checkoutów:

- `ai-dev-cli-tools/.venv/Scripts/ai-dev.exe scan`;
- `freelance-dev-suite/packages/intake/analyzer.py::analyze_project`, uruchomione z checkoutu przez `PYTHONPATH`, z `AI_DEV_EXECUTABLE` wskazującym powyższy plik;
- analizator freelance wywołał scan, map, pełną walidację i budowanie kontekstu ai-dev;
- niezależne uruchomienie pytest w `AdaptiveChessAI/venv`, Ruff i mypy z runtime ai-dev, mała pełna seria eksperymentów oraz sondy GUI/backendu.

Raport automatyczny: `.ai/reports/freelance-adaptivechess-audit.json`. Jego szacunek 3–8 godzin jest ogólną heurystyką narzędzia, **nie wyceną realizacji poniższego planu**. Wskazanie braku frameworka również nie zastępuje inspekcji: PySide6 jest obecny. Nie mierzono kosztów ani oszczędności tokenowych.

### Wyniki wykonanych sprawdzeń

| Sprawdzenie | Wynik i ograniczenie |
|---|---|
| Pełny pytest w środowisku projektu | **271 passed, 3.94 s**; Qt offscreen; po uruchomieniu poza blokadą sandboxa katalogów tymczasowych |
| Ruff na `src scripts tests` | Przeszedł |
| Mypy na `src scripts tests` | Przeszedł, 104 pliki; `ignore_missing_imports` ogranicza siłę tej kontroli |
| Ruff na całym repo przez ai-dev | Błąd: pusty `notebooks/results_analysis.ipynb` nie jest poprawnym JSON-em notebooka |
| Pytest przez automatycznie wybrany runtime ai-dev | 30 błędów zbierania, m.in. brak `chess` i `pandas`; wybrano środowisko narzędzia zamiast projektu |
| Pierwsze bezpośrednie próby pytest | Najpierw brak katalogu nadrzędnego basetemp, następnie WinError 5; to problemy uruchomienia, nie 41 usterek produktu |
| Pełny pipeline eksperymentów | Przeszedł: 14 partii, 7 konfiguracji, CSV, metadane, raporty, PNG i zbiorczy Markdown |
| GUI | Utworzenie ekranów, gra i reset sprawdzone programowo; obejrzano render ekranu gry |

Mała seria: `--matches 2 --max-half-moves 20 --depths 1`. W 11 z 14 partii osiągnięto limit półruchów. Jest to dowód działania pipeline'u, nie wynik naukowy o przewadze któregoś agenta. Boty losowe nie mają tu zapisanego seeda, więc ponowne uruchomienie może dać inne wyniki.

Dowody lokalne: `.ai/reports/audit-20260914/` zawiera `probes.json`, `pytest-permitted.log`, `pytest-permitted.xml`, `suite.log` oraz rendery GUI. Sonda: `.ai/audit_20260914_probe.py`. Wyniki serii: `results/audit-20260914-smoke/`. Te katalogi są ignorowane przez Git; najważniejsze fakty zachowano w tym raporcie.

Render Qt offscreen początkowo nie znajdował fontów. Do samej sondy dodano jawne ładowanie lokalnych fontów Segoe UI i Segoe UI Symbol. Nie zmieniono aplikacji. Nie przeprowadzono pełnego ręcznego testu na monitorze użytkownika, różnych DPI ani długiego testu wydajności.

## 3. Najważniejsze rozbieżności z celem

### P0 — doświadczenie człowieka nie przechodzi do następnej partii ani turnieju

`src/adaptive_chess/ui/screens/game_screen.py:249` tworzy bota przez `create_bot_for_gui`. Fabryka w `src/adaptive_chess/ui/bot_factory.py:21` tworzy nowy `AdaptiveMinimaxBot` bez przekazanego wcześniejszego profilu. `prepare_for_new_game` usuwa sesję. Nie ma repozytorium stanu agenta ani wczytywania checkpointu.

**Reprodukcja:** start gry adaptive, człowiek gra `e2e4`, bot odpowiada. Profil ma `observed_moves=1`, `center_moves=1`. Po ponownym rozpoczęciu gry nowy bot ma `observed_moves=0`. To inna instancja. Zapis JSON/CSV partii nie zapisuje stanu uczenia.

Z kolei `scripts/run_static_vs_adaptive_series.py:200` tworzy własne nowe profile dla serii bot–bot. Mają one ciągłość pomiędzy partiami danej konfiguracji kolorów, ale nie pochodzą z gier człowieka. GUI i eksperyment nie tworzą obecnie wspólnego procesu badawczego.

### P0 — nie ma porównania kilku metod uczenia

`RandomBot` i `StaticMinimaxBot` nie uczą się. Mogą być wartościowymi punktami odniesienia, ale nie można opisywać ich jako konkurencyjnych metod uczenia.

`AdaptiveMinimaxBot` aktualizuje cztery liczniki: obserwowane ruchy, bicia, szachy i wejścia na centralne pola. `adaptive_scoring.py` ma ręcznie ustalone progi 0.30/0.30/0.15 oraz stałe korekty ocen. Jest to prosta adaptacja do profilu przeciwnika. Nie ma uczenia wag na wyniku partii, predykcji jakości ruchu ani modelu trenowanego na przykładach. `src/adaptive_chess/learning/__init__.py` jest pusty.

Ważne ograniczenie: wysoki udział bić może wynikać z pozycji stwarzanych przez samego bota. Obecny profil nie normalizuje zachowania względem dostępnych okazji. Pojedynczy ruch do centrum daje od razu współczynnik 1.0 i aktywuje regułę. Rosnąca liczba obserwacji nie gwarantuje rosnącej siły gry.

### P0 — brak rozdzielenia treningu i oceny

`MatchRunner` zawsze wywołuje `observe_move` obu botów (`match_runner.py:162`), a adaptive zawsze aktualizuje profil przeciwnika (`adaptive_minimax_bot.py:96`). Sonda czterech półruchów podniosła licznik z 0 do 2. Nie ma przełącznika `train/eval` ani ochrony checkpointu przed zmianą.

Dzisiejsze serie badają adaptację podczas gry z botami. Nie odpowiadają na pytanie, jak mocny jest stan agenta po X partiach z człowiekiem. W docelowej ocenie wynik nie może zależeć od tego, który przeciwnik turniejowy wcześniej zmodyfikował profil.

### P1 — pomieszane znaczenie wyniku i ograniczone miary

`match_runner.py:135` zapisuje osiągnięcie limitu jako `1/2-1/2`, choć partia mogła nie zakończyć się remisem według zasad. Osobno adjudykacja materiałowa może nadać jej wygraną. Ten podział jest opisany i częściowo poprawnie raportowany, ale etykieta „wynik formalny” jest myląca przy przerwaniu technicznym.

Docelowo zapisywać osobno wynik szachowy, powód zakończenia i opcjonalną ocenę techniczną. Przerwane partie nie powinny po cichu dostawać nagrody za zwycięstwo ani być usuwane z raportu. Ustalić przed eksperymentem politykę limitów i pokazywać liczbę takich przypadków. Przewaga materiału nie dowodzi, że bot potrafi wygrać końcówkę.

Statystyki agregują głównie białe/czarne/remisy, materiał i długość partii. Brakuje wyniku konkretnego agenta, postępu względem jego wersji początkowej, liczby partii treningowych, czasu uczenia i przedziałów niepewności.

### P1 — potwierdzony błąd oceny automatycznego remisu

`src/adaptive_chess/evaluation/position.py:19` zeruje ocenę pata i niewystarczającego materiału, ale nie wszystkich automatycznych remisów. Przeszukiwanie zatrzymuje się na `board.is_game_over()`, po czym korzysta z tej oceny.

**Reprodukcja:** FEN `7k/8/8/8/8/8/R7/K7 w - - 150 76` jest poprawny, `is_game_over()` daje True, wynik wynosi `1/2-1/2`, lecz ocena dla białych to **5.6**, zamiast 0. Dotyczy to wartości pozycji w wyszukiwaniu i może zniekształcać wybór ruchu prowadzącego do remisu. Warto dodać także regresję dla pięciokrotnego powtórzenia z zachowaną historią ruchów.

### P1 — brak odtwarzalności i odporności zapisu

- `RandomBot` używa globalnego `random.choice`; nie ma osobnego RNG, seeda agenta i zapisanego stanu generatora.
- Nie ma identyfikatorów kampanii, uczestnika, trwałej instancji agenta, checkpointu ani zbioru treningowego.
- Metadane zawierają czas UTC i nazwy wersji algorytmów, ale nie SHA kodu, wersji środowiska, stanu RNG i powiązań trening–ocena.
- Eksport człowieka nie przechowuje początkowego FEN, chociaż sesja przyjmuje niestandardową pozycję. Utrudnia to jednoznaczną rekonstrukcję dowolnej partii.
- Człowiek zapisuje partię ręcznie dopiero z podsumowania. Brak autosave i odtwarzania po zamknięciu aplikacji.
- CSV/JSON zapisują się przez nadpisanie; dwa eksporty tej samej konfiguracji w tej samej sekundzie mogą użyć identycznej nazwy. Serie mają stałe nazwy plików, a dane przechowują w pamięci do eksportu. Awaria długiej serii może stracić niezapisany postęp.
- Powtarzanie deterministycznych botów z identycznego startu nie daje automatycznie niezależnych prób. Potrzebne są ustalone pary otwarć i jawne źródła losowości.

### P1/P2 — GUI obsługuje partię, ale nie proces badawczy

Na plus: osobne ekrany, legalne ruchy, obracanie planszy, historia, ustawienia, podsumowanie i eksport. Eksperymenty działają w `QProcess`, więc mają już oddzielony proces obliczeniowy.

Problemy:

- Brak kampanii, licznika „partia 7/20”, listy wytrenowanych agentów i możliwości wznowienia treningu.
- Ruch bota w grze człowieka wykonywany jest synchronicznie w obsłudze kliknięcia. Głębsze wyszukiwanie blokuje obsługę GUI. Jedna próbka pozycji początkowej przy depth=3 zajęła około 0.24–0.28 s dla static i 0.55–0.59 s dla adaptive; to ilustracja, nie benchmark całej partii.
- Adaptive nie przenosi najlepszego alpha pomiędzy kandydatami ruchu głównego tak jak static. Równa głębokość nie oznacza identycznej pracy obliczeniowej.
- W renderze figury są bardzo małe; ogólny styl `QWidget {font-size:14px}` koliduje z intencją `setPointSize(28)` dla pól. Plansza rozciąga się bez wymuszenia proporcji 1:1 i nie ma współrzędnych pól.
- Statusy mieszają polski i angielski; FEN zajmuje ważne miejsce w podstawowym widoku, podczas gdy nie ma informacji o uczeniu.
- Promocja wybiera domyślnie hetmana; użytkownik nie może świadomie wybrać innej figury.
- „Zakończ i podsumuj” daje `*`, nie poddanie. Potrzebne odrębne działania: poddaj, przerwij, wznów.
- Wyniki są przeglądarką plików, a nie tabelą turnieju i krzywą uczenia. PNG otwiera się zewnętrznie.
- `QProcess.terminate()` nie zapewnia zapisu i wznowienia, a full suite uruchamia kolejne podprocesy. Obsługę anulowania całego drzewa trzeba zweryfikować przed długimi eksperymentami; nie odtwarzano tej sytuacji w audycie.

### P2 — dokumentacja i dostarczanie aplikacji

README i `docs/mvp_status.md` nadal twierdzą, że GUI i gra człowieka nie istnieją. `docs/architecture.md` i notebook są puste. Starszy plan GUI miesza elementy już wykonane z przyszłymi. To utrudnia ocenę postępu i może wprowadzić promotora w błąd.

Brak CI w repo, lockfile'a, jednoznacznej konfiguracji paczki desktopowej i zależności runtime w sekcji `[project]`. Skrypty ręcznie dopisują `src` do ścieżki importów. `get_project_root()` zakłada układ checkoutu z katalogiem `scripts`, co trzeba zmienić przed pakowaniem aplikacji. Testy działają lokalnie, ale nie stanowią dowodu instalowalności na czystym komputerze.

W przejrzanej aplikacji nie ma serwera HTTP, logowania ani integracji z chmurą, więc nie ma uzasadnienia dla projektowania autoryzacji API na obecnym etapie. Najistotniejsze ryzyka danych to utrata i pomieszanie wyników. Przyszłe importy modeli powinny mieć walidowany format; nie należy opierać wymiany niezaufanych modeli na wykonywalnej deserializacji. Nie wykonano audytu zależności pod kątem znanych CVE ani przeglądu całej historii Git pod kątem sekretów.

## 4. Co dokładnie ma mierzyć praca

Proponowany temat: **„Projekt i implementacja platformy do porównania metod adaptacji agentów szachowych na podstawie rozgrywek z graczem nieeksperckim”**.

Roboczo interpretuję „zastąpić człowieka” jako osiągnięcie co najmniej jego skuteczności w grze. Naśladowanie jego stylu jest innym celem i wymaga innych miar. Aplikacja może obsługiwać oba, ale praca powinna wskazać jeden jako główny.

| Pytanie | Potrzebny pomiar |
|---|---|
| Czy bot nauczył się skuteczniej grać przeciw mnie? | Nowe partie z tym człowiekiem, stan bota zamrożony, porównanie z checkpointem 0 |
| Czy stał się ogólnie silniejszy? | Stały zestaw przeciwników i pozycji, oceniany przed treningiem i po nim |
| Który wytrenowany agent wygrywa z pozostałymi? | Turniej zamrożonych checkpointów przy wspólnym protokole |
| Czy imituje moje wybory? | Predykcja ruchów człowieka na osobnych partiach, nie na ruchach losowo wydzielonych z tych samych partii |
| Ile doświadczenia potrzebuje? | Ocena przy kilku checkpointach oraz licznik treningowych partii, ruchów i czasu |

Zwycięzca turnieju może być najsilniejszy już przed treningiem. Dlatego kluczowe są zarówno wynik końcowy, jak i **przyrost względem własnego punktu startowego**. Sukces projektu nie wymaga, aby każdy agent ostatecznie wygrał z człowiekiem: wynik „nie osiągnął progu w badanym budżecie” jest prawidłową obserwacją.

## 5. Docelowy przebieg w aplikacji

1. **Nowa kampania:** pseudonim uczestnika, liczba partii X na agenta, metody uczenia, budżet ruchu, seed i punkty kontrolne. Program pokazuje przewidywaną liczbę wszystkich gier.
2. **Pomiar początkowy:** zapis checkpointu 0 i automatyczna ocena na ustalonym zestawie. Partie kontrolne z człowiekiem, jeśli głównym celem jest przewyższenie tego człowieka.
3. **Trening:** aplikacja wskazuje następnego agenta i kolor, np. „TD, partia 7/20, grasz czarnymi”. Ruchy i wynik zapisują się automatycznie. Agent zachowuje doświadczenie po restarcie.
4. **Punkty kontrolne:** np. po 5, 10 i 20 partiach tworzony jest niezmienny checkpoint. Automatyczna ocena odbywa się na jego kopii, z wyłączonym uczeniem. Trening może później kontynuować stan treningowy.
5. **Turniej:** każdy agent gra z każdym z tego samego etapu treningu, po obu stronach tych samych otwarć. GUI pokazuje kolejkę, bieżącą partię, tabelę i możliwość bezpiecznej pauzy.
6. **Raport:** końcowy ranking, przyrost siły, krzywe względem liczby gier, niepewność, liczba partii przerwanych, zużyty czas, eksport CSV/JSON/PGN i opis protokołu.

Osobny „Tryb swobodnej gry” może pozostać, ale nie powinien zmieniać agentów z zakończonego badania.

## 6. Agenci — proponowany zakres

Najpierw uruchomić pełną kampanię z obecnym adaptive i static. Dopiero wtedy dodawać nowe metody w tym samym interfejsie. Docelowa, rozsądna wersja pracy to trzy metody plus kontrola:

| Agent | Czego się uczy | Dane i ograniczenia |
|---|---|---|
| StaticMinimax | Nic; kontrola | Stałe parametry, wspólny budżet wyszukiwania |
| ProfileAdaptive | Tendencji przeciwnika | Rozwinąć obecny model o minimalną liczbę obserwacji i wygładzanie; jawnie nazywać adaptacją heurystyczną |
| ImitationAgent | Preferencji ruchów człowieka | Model rankingu legalnych ruchów na cechach pozycji/ruchu; uczy się z wyborów człowieka, nie zakłada, że są optymalne |
| TDAgent | Wartości pozycji przy grze | Na początek mały liniowy model wartości z aktualizacją TD; wynik partii i przejścia pozycji, z jednoznaczną perspektywą koloru |

RandomBot zachować do smoke testów i sanity checków. Mocniejszy stały silnik może później służyć jako przeciwnik lub niezależny oceniający, ale zwiększanie jego siły nie jest uczeniem z człowieka.

ImitationAgent powinien odróżniać użycie modelu do własnych ruchów od modelowania odpowiedzi konkretnego człowieka. Wybrać i zapisać jeden wariant eksperymentalny. Nie obiecywać, że samo kopiowanie słabszego gracza spowoduje przekroczenie jego poziomu. Literatura o imitacji opisuje też problem zmiany rozkładu odwiedzanych stanów podczas samodzielnej gry: [Ross, Gordon, Bagnell, 2011](https://proceedings.mlr.press/v15/ross11a.html).

TD jest propozycją małego eksperymentu, nie gwarancją sukcesu przy kilkunastu partiach. Klasyczny TD-Gammon pokazuje zastosowanie uczenia wartości w grze i treningu self-play; dotyczy backgammona, więc nie dowodzi skuteczności na małych danych szachowych: [Tesauro, 1995](https://www.cnbc.cmu.edu/~plaut/IntroPDP/papers/Tesauro95ComACM.TDGammon.pdf).

Self-play, pretraining i oceny z silnika należy traktować jako oddzielne warunki. Gdy jeden agent dostanie tysiące dodatkowych partii, nie można twierdzić, że wszyscy nauczyli się wyłącznie na tych samych X grach z człowiekiem. Nie rekomenduję dużej sieci ani pełnego AlphaZero jako pierwszego etapu tej pracy.

## 7. Protokół eksperymentu

### Budżet i kolejność

Roboczy pilotaż: 3 metody uczące się × 10 partii treningowych = 30 partii człowieka, **plus osobny budżet gier kontrolnych**. Dopiero po pilotażu zdecydować o X=20 lub większym. Wartość 10 nie jest wyliczeniem wymaganej próby statystycznej.

Grać z agentami naprzemiennie w zrównoważonej kolejności i zmieniać kolory. W przeciwnym razie trzeci bot dostaje innego człowieka: bardziej doświadczonego lub zmęczonego. Przy kilku uczestnikach rotować kolejność między uczestnikami. Przy jednym uczestniku opisywać badanie jako studium przypadku, nie wynik dla wszystkich amatorów.

Równa liczba gier nie daje identycznej liczby ruchów ani tych samych pozycji. Raportować wszystkie te wielkości. Główny eksperyment może zachować wymagane gry interaktywne z każdym agentem. Dodatkowym, oddzielnym eksperymentem może być trening metod na wspólnym zapisanym zbiorze partii; to odpowiada na inne pytanie o porównywalność danych.

### Ocena i turniej

- Zapisać przed treningiem zestaw przeciwników, listę otwarć i ustawienia. Nie dobierać ich po obejrzeniu wyników.
- Każda para otwarcie–przeciwnik powinna być grana z zamianą kolorów. Różne otwarcia/seed i osobne przebiegi stanowią źródła zmienności; kopiowanie identycznej deterministycznej partii nie zwiększa dowodu.
- Dla 4 uczestników turnieju i 5 otwarć: `4×3/2 × 5 × 2 = 60` partii na checkpoint. Ustalić liczbę przed uruchomieniem; wersje checkpointów 0/5/10 oceniać jako osobne turnieje lub bloki.
- Główny wynik agenta: `(wygrane + 0.5 × remisy) / liczba sklasyfikowanych partii`, z osobnym zestawieniem przerwanych i ustaloną polityką ich traktowania. Nie selekcjonować wygodnych zakończeń.
- Wspólny budżet obliczeniowy: czas na ruch albo liczba węzłów z jednakową polityką limitów; dodatkowo raportować faktyczny czas i głębokość. Najprostszy etap wstępny może utrzymać stałe depth, ale trzeba ujawnić różnicę kosztu metod.
- Rejestrować wynik początkowy, końcowy i różnicę, a także wynik przeciw każdemu przeciwnikowi. Sam ranking może ukryć zależności typu A pokonuje B, B pokonuje C.

### „Ile czasu do pokonania człowieka”

Jedna wygrana to osobna miara „pierwsze zwycięstwo”, a nie dowód trwałej przewagi. Dla silniejszego wniosku ustalić z góry np. punktowy próg skuteczności 60%, wielkość bloku gier kontrolnych i metodę oceny niepewności. Wartości są propozycją protokołu do uzgodnienia z promotorem, nie standardem naukowym.

Jeżeli człowiek gra tylko z checkpointami 0, 10 i 20, można wykazać przekroczenie progu przy którymś pomiarze albo przedział między nimi; nie można podać dokładnej wcześniejszej partii treningowej. Brak przekroczenia oznacza „nie osiągnięto w budżecie X”, bez ekstrapolowania gwarantowanego terminu.

Niepewność liczyć z uwzględnieniem bloków otwarć, przebiegów i uczestników, np. odpowiednio grupowanym bootstrapem. Przy pojedynczym człowieku i małej liczbie gier prezentować przede wszystkim wyniki opisowe. Wielokrotne sprawdzanie progu zwiększa ryzyko przypadkowego sukcesu; zaplanować osobny końcowy blok potwierdzający i nie stroić na nim parametrów.

## 8. Architektura do wdrożenia

Przepływ: `GUI → CampaignService → GameSession / TrainingService / EvaluationRunner → repozytorium danych → raporty`.

| Element | Odpowiedzialność |
|---|---|
| Campaign | Protokół, uczestnik, status, harmonogram, postęp i wznowienie |
| AgentSpec | Metoda, wersja, konfiguracja początkowa i budżet |
| AgentState / Checkpoint | Stan uczenia, RNG, pochodzenie, liczba gier/ruchów, hash |
| GameRecord / MoveRecord | Partia i ruchy niezależne od ekranu GUI |
| TrainingService | Aktualizacja tylko stanu treningowego; obsługa końca/przerwania gry |
| EvaluationRunner | Wczytanie checkpointu bez zmiany stanu; kontrola hash przed/po |
| TournamentRunner | Harmonogram każda para/otwarcie/kolor, rezultaty i wznowienie |
| AnalysisService | Agregacja po agentach, checkpointach i uczestnikach; porównania |

Minimalny kontrakt agenta: `choose_move`, `observe_transition`, `end_game`, `set_mode`, `save_state`, `load_state`. To propozycja; dopasować nazwy do istniejącego `BaseBot`, zachowując prostotę adapterów. `choose_move` w trybie oceny nie może trenować ukrytych parametrów; zamrożenie musi objąć także cache uczenia, optimizer i normalizację cech, jeśli się pojawią.

Lokalne SQLite jest rozsądnym magazynem kampanii, partii i ruchów; checkpointy mogą być wersjonowanymi plikami JSON/NPZ z hashami. Zapisywać ruchy transakcyjnie i finalizować checkpoint atomowo. Eksport CSV/PGN jest formatem wymiany, a nie jedynym źródłem prawdy. Zaprojektować idempotentny zapis partii i aktualizacji, aby restart nie powodował dwukrotnego treningu.

Minimalne dane: campaign_id, participant_id, agent_id, checkpoint_id, phase, training_games_seen, training_moves_seen, initial_fen, ruchy UCI, wynik, termination_reason, seed/RNG, ustawienia, wersje bibliotek, SHA kodu i informacja o lokalnych zmianach, czasy ruchów/treningu, identyfikator otwarcia. Uczestnika identyfikować pseudonimem; wszystkie dane mogą pozostawać lokalnie.

Obliczenia bota przenieść poza wątek GUI, najlepiej do kontrolowanego procesu z anulowaniem i limitem. Nie przekazywać workerowi mutable stanu widgetów. Potrzebne zdarzenia: ruch rozpoczęty/zakończony, zapis potwierdzony, checkpoint gotowy, partia zakończona/przerwana.

## 9. Plan wykonania i kryteria odbioru

| Etap | Zakres | Sprawdzalny warunek zakończenia |
|---|---|---|
| A. Zasady badania i stan repo | Krótki protokół; poprawa opisu istniejących funkcji; poprawny notebook; środowisko i CI | Jeden aktualny opis, powtarzalne uruchomienie testów; zdefiniowane trening/ocena i wynik |
| B. Stan agenta | Trwały profil obecnego adaptive, checkpoint 0, zapis/wczytanie, train/eval | Po dwóch partiach licznik rośnie; restart go zachowuje; ocena nie zmienia checkpointu |
| C. Kampania i zapis | Harmonogram X partii, SQLite, autosave, wznowienie, identyfikatory | Zamknięcie w połowie gry i wznowienie nie gubi ruchu ani nie dubluje uczenia |
| D. Wygodna gra | Duże figury, kwadratowa plansza, współrzędne, promocja, poddanie, worker | Pełna partia bez zawieszania UI; użytkownik widzi agenta, fazę i postęp |
| E. Turniej checkpointów | Pary kolorów/otwarć, wynik i powód zakończenia, limity, bezpieczna pauza | Pełny harmonogram bez braków/duplikatów; wznowienie; hash wszystkich modeli bez zmian |
| F. Druga i trzecia metoda | Imitation i TD, jeden wspólny kontrakt, kontrola danych i hiperparametrów | Parametry naprawdę się aktualizują; zapis/wczytanie odtwarza model; brak uczenia w eval |
| G. Analiza i badanie | Krzywe uczenia, baseline, raport, pilotaż, końcowy protokół | Raport pozwala odtworzyć wynik z surowych danych i określa granice wniosków |

**Pierwszy sensowny przyrost produktu:** obecny adaptive zapamiętuje gry z człowiekiem, kampania pokazuje X partii, a następnie przekazuje zapisany checkpoint do małego turnieju przeciw static. To bezpośrednio realizuje rdzeń wizji i pozwala ocenić użyteczność przed rozbudową algorytmów.

Priorytetowe regresje: utrzymanie stanu między partiami i restartami, niezmienność checkpointu w ocenie, poprawność wszystkich remisów, izolacja uczestników, wznowienie po awarii bez powtórnej aktualizacji, odtworzenie seeda, kompletność harmonogramu, brak przecieku gier testowych do treningu. Test „agent zmienia wagi” nie dowodzi poprawy gry; ten wniosek musi pochodzić z eksperymentu.

Do późniejszego etapu odłożyć chmurę, logowanie, aplikację webową, duże sieci, automatyczne strojenie na wynikach końcowych i rozbudowane rankingi online. Przed finalnym pakowaniem sprawdzić uruchomienie bez checkoutu i dostępności deweloperskiego `venv`.

## 10. Literatura i związek z ustaleniami

- [Dokumentacja python-chess](https://python-chess.readthedocs.io/en/stable/) — zasady automatycznych remisów i możliwości biblioteki; repo powinno konsekwentnie stosować je również w ocenie pozycji.
- [Ross, Gordon, Bagnell: A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning, 2011](https://proceedings.mlr.press/v15/ross11a.html) — tło ograniczeń uczenia przez imitację w procesach sekwencyjnych.
- [Tesauro: Temporal Difference Learning and TD-Gammon, 1995](https://www.cnbc.cmu.edu/~plaut/IntroPDP/papers/Tesauro95ComACM.TDGammon.pdf) — przykład uczenia funkcji wartości w grach; inspiracja metodyczna, nie prognoza wyniku tego projektu.

Dobór agentów, harmonogram i architektura powyżej są propozycją projektową wynikającą z audytu. Nie są istniejącymi funkcjami aplikacji ani potwierdzonymi rezultatami badania.
