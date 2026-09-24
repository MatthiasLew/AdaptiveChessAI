"""Local interface catalogue. User data and raw exports are never translated."""

from html import escape

from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QTabWidget,
    QTextEdit,
    QWidget,
)

_language = "pl"
EN = {
    "Brak zakończonej partii.": "No finished game yet.",
    "Graj ponownie": "Play again",
    "Zapisz partię": "Save game",
    "Końcowy FEN": "Final FEN",
    "Końcowy materiał": "Final material balance",
    "Liczba półruchów": "Individual moves",
    "Podsumowanie partii": "Game summary",
    "Inteligentne szachy. Adaptacyjna nauka. Eksperymenty.": "Chess. Adaptive learning. Experiments.",
    "Kliknij własną figurę, a potem pole docelowe. Po ruchu człowieka bot odpowie automatycznie.": "Click your piece, then its destination. The bot will reply automatically.",
    "Profil, imitacja, TD i kontrola statyczna. 4X partii treningowych.": "Profile, imitation, TD and static control. 4X training games.",
    "Utwórz kampanię albo wczytaj zapisany plik.": "Create a campaign or load a saved file.",
    "Wybierz ustawienia i kliknij „Nowa gra”.": "Choose your settings and click New game.",
    "Losowy": "Random",
    "Statyczny": "Static",
    "Adaptacyjny": "Adaptive",
    (
        "Wybierz porównanie i liczbę partii, a następnie rozpocznij. "
        "Wyniki pojawią się tutaj."
    ): (
        "Choose a comparison and number of games, then start. Results will appear here."
    ),
    (
        "Przerwane partie nie oznaczają remisu ani zwycięstwa. Kolor "
        "dotyczy strony na planszy."
    ): ("Stopped games are not draws or wins. Colors refer to sides on the board."),
    "Pokazano pierwsze 200 partii. Pełne dane znajdują się w pliku.": "Showing the first 200 games. The file contains all results.",
    "Podsumowanie wszystkich porównań": "All comparisons overview",
    "Raport kampanii": "Campaign report",
    "Postępy uczenia": "Learning progress",
    "Tabela turnieju": "Tournament standings",
    "Wyniki przeciw człowiekowi": "Results against the human",
    "Zapis kampanii": "Campaign record",
    "Partie przerwane limitem": "Games stopped at the move limit",
    "Ocena pomocnicza pozycji": "Auxiliary position evaluation",
    "Przewaga figur na końcu gry": "Material advantage at game end",
    "Wartość": "Value",
    "Partie treningowe": "Training games",
    "Wynik punktowy": "Score",
    "Wygrane": "Wins",
    "Przegrane": "Losses",
    "Punkty": "Points",
    "Model po liczbie partii": "Model after games",
    "Pełne pary kolorów": "Complete color pairs",
    "Zmiana od początku nauki": "Change since baseline",
    "Dolna granica niepewności": "Lower uncertainty bound",
    "Górna granica niepewności": "Upper uncertainty bound",
    "Sprawdzone pozycje": "Positions searched",
    "Czas wyboru ruchów (s)": "Move selection time (s)",
    "Czas uczenia (s)": "Learning time (s)",
    "Aktualizacje modelu": "Model updates",
    "Limit ruchów obu stron": "Move limit for both sides",
    "Rodzaj porównania": "Comparison type",
    "Data utworzenia (UTC)": "Created (UTC)",
    "Wybierz raport lub wykres po lewej stronie.": "Choose a report or chart on the left.",
    "Graj": "Play",
    "Gra swobodna": "Free play",
    "Eksperymenty": "Experiments",
    "Wyniki": "Results",
    "Ustawienia": "Settings",
    "Wyjście": "Exit",
    "Powrót do menu": "Back to menu",
    "Wstecz": "Back",
    "Zagraj i trenuj swoich agentów": "Play and train your agents",
    "Najpierw wybierz nową kampanię albo swój zapis.": "Create a campaign or load your saved progress.",
    "Nowa kampania": "New campaign",
    "Wczytaj kampanię…": "Load campaign…",
    "Wróć do bieżącej kampanii": "Return to current campaign",
    "Nowa kampania — ustawienia przed grą": "New campaign — before you play",
    "Twój pseudonim": "Your nickname",
    "Partie na każdego z 4 agentów": "Games per agent (4 agents)",
    "Głębokość": "Search depth",
    "Budżet węzłów / ruch": "Search nodes per move",
    "Otwarcia UCI (oddziel ;)": "Opening moves (separate with ;)",
    (
        "Postęp zapisuje się po każdym ruchu. Kolory zmieniają się co rundę."
    ): "Every move is saved. Colors alternate each round.",
    "Utwórz kampanię i graj…": "Create campaign and play…",
    "Rozpocznij / wznów partię": "Start / resume game",
    "Poddaj partię": "Resign",
    "Ruchy": "Moves",
    "Ocena i raport": "Evaluation",
    "Limit półruchów": "Half-move limit",
    "Agent kontrolny": "Evaluation agent",
    "Checkpoint": "Saved model",
    "Oceń checkpointy / turniej": "Evaluate / tournament",
    "Partia kontrolna (bez nauki)": "Control game (no learning)",
    "Eksportuj raport i partie": "Export report and games",
    "Zatrzymaj ocenę / turniej": "Stop evaluation / tournament",
    "Zapisano automatycznie • Wróć": "Saved automatically • Back",
    "Rozpocznij następną partię": "Start next game",
    "Rozpocznij pierwszą partię": "Start first game",
    "Domyślny bot": "Default opponent",
    "Domyślny kolor gracza": "Your default color",
    "Siła przewidywania ruchów": "Search depth",
    "Domyślny folder eksperymentów": "Default results folder",
    "Język interfejsu": "Interface language",
    "Wygląd": "Appearance",
    "Ciemny": "Dark",
    "Jasny": "Light",
    "Pauza przed ruchem bota": "Pause before the bot moves",
    (
        "Uruchamiaj na pełnym ekranie (F11 przełącza, Esc wraca do okna)"
    ): "Start in fullscreen (F11 toggles, Esc returns to window)",
    "Zapisz ustawienia": "Save settings",
    "Przywróć domyślne": "Restore defaults",
    "Ustawienia zapisane.": "Settings saved.",
    "Białe": "White",
    "Czarne": "Black",
    "Wyniki i raporty": "Results and reports",
    "Folder wyników": "Results folder",
    "Wczytaj": "Load",
    "Wybierz folder": "Choose folder",
    "Otwórz folder": "Open folder",
    "Otwórz wybrany plik": "Open selected file",
    "Raporty i wykresy": "Reports and charts",
    "Podsumowanie": "Summary",
    "Pokaż pliki techniczne": "Show technical files",
    "Wybierz folder wyników i kliknij „Wczytaj”.": "Choose a results folder and click Load.",
    "Porównaj boty": "Compare bots",
    "Co chcesz porównać?": "What would you like to compare?",
    "Wszystkie dostępne porównania": "All available comparisons",
    "Losowy z losowym": "Random vs random",
    "Losowy ze statycznym": "Random vs static",
    "Losowy z adaptacyjnym": "Random vs adaptive",
    "Statyczny z adaptacyjnym": "Static vs adaptive",
    "Liczba partii": "Number of games",
    "Maksymalna liczba ruchów obu stron": "Maximum moves by both sides",
    "Poziom przewidywania": "Search depth",
    "Rozpocznij porównanie": "Start comparison",
    "Anuluj": "Cancel",
    "Otwórz folder wyników": "Open results folder",
    "Zobacz wyniki": "View results",
    "Przebieg porównania": "Comparison progress",
    "Szczegóły techniczne": "Technical details",
    "Status": "Status",
    "Gotowe do rozpoczęcia.": "Ready to start.",
    "Porównanie trwa…": "Comparison in progress…",
    "Porównanie zakończone. Wyniki są gotowe.": "Comparison completed. Results are ready.",
    "Porównanie zatrzymane.": "Comparison stopped.",
    (
        "Nie udało się ukończyć porównania. Otwórz szczegóły techniczne."
    ): "The comparison failed. Open technical details.",
    ("Boty zagrają ze sobą automatycznie. Nie musisz wykonywać ruchów."): (
        "Bots will play automatically. You do not need to make any moves."
    ),
    ("Porównanie pomocnicze. Aby badać uczenie z Twoich partii, wybierz Graj."): (
        "Auxiliary comparison. To study learning from your games, choose Play."
    ),
    (
        "Jedna jednostka to ruch jednej strony. Mały limit często "
        "przerywa grę przed rozstrzygnięciem."
    ): (
        "Each unit is one move by one side. A low limit often stops "
        "games before a result."
    ),
    "Większa wartość oznacza dłuższe obliczenia.": "Higher values require more computation time.",
    "Gra z botem": "Play against a bot",
    "Nowa gra": "New game",
    "Zakończ i podsumuj": "Finish and summarize",
    "Wyczyść partię": "Clear game",
    "Ustawienia gry": "Game settings",
    "Kolor gracza": "Your color",
    "Głębokość minimaxa": "Search depth",
    "Historia ruchów": "Move history",
    "Bot": "Opponent",
    "Wygrana!": "You won!",
    "Przegrana": "You lost",
    "Remis": "Draw",
    "Partia przerwana": "Game stopped",
    "Poddanie partii": "Resignation",
    "Koniec według reguł szachowych": "Game ended by chess rules",
    "Twój ruch.": "Your turn.",
    "Ruch bota.": "Bot's turn.",
    "Twój ruch zapisany. Bot za chwilę odpowie…": "Your move is saved. The bot will reply shortly…",
    "Bot myśli… Ruchy są zapisywane automatycznie.": "The bot is thinking… Moves are saved automatically.",
    "Kampania gotowa. Rozpocznij pierwszą partię.": "Campaign ready. Start the first game.",
    "Partie": "Games",
    "Wygrane białych": "White wins",
    "Wygrane czarnych": "Black wins",
    "Remisy": "Draws",
    "Przerwane limitem": "Stopped at move limit",
    "Brak zakończonych partii.": "No completed games yet.",
    "Ustawienia uruchomienia": "Run settings",
    "Dane techniczne": "Technical data",
    "Szczegóły partii": "Game details",
    "Wynik": "Result",
    "Białymi": "White player",
    "Czarnymi": "Black player",
    "Zakończenie": "Termination",
    "Liczba ruchów": "Moves played",
}

EN.update(
    {
        "Kampania badawcza": "Research campaign",
        "Graj, ucz i porównuj.": "Play, train and compare.",
        "Pracownia adaptacyjnych agentów szachowych": "Adaptive chess research workspace",
        "Trenuj cztery metody na swoich partiach. Wznawiaj zapis i oceniaj checkpointy.": "Train four methods on your games. Resume a campaign and evaluate checkpoints.",
        "Zagraj z wybranym botem poza kampanią.": "Play against a bot outside the research campaign.",
        "Uruchom automatyczne porównania botów.": "Run automated bot comparisons.",
        "Przejrzyj podsumowania, wykresy i tabele badań.": "Explore research summaries, charts and tables.",
        "Konfiguracja treningu": "Training configuration",
        "Parametry zaawansowane": "Advanced parameters",
        "Plan kampanii": "Campaign plan",
        "{games} partii / metodę \u00d7 4 = {total} partii treningowych": "{games} games / method \u00d7 4 = {total} training games",
        "Głębokość {depth} • Węzły / ruch {nodes} • Seed {seed}": "Depth {depth} • Nodes / move {nodes} • Seed {seed}",
        "Ocena checkpointów i turniej wymagają dodatkowych gier.": "Checkpoint evaluation and the tournament require additional games.",
        "Cztery metody": "Four methods",
        "Gra": "Game",
        "Badania / pliki": "Research / files",
        "Bieżąca partia": "Current game",
        "Pozycja techniczna": "Technical position",
        "Raporty i pliki": "Reports and files",
        "Rozkład wyników": "Outcome distribution",
        "Wczytaj folder, aby zobaczyć statystyki.": "Load a folder to see statistics.",
        "Pełny zestaw: cztery porównania botów.": "Full suite: four bot comparisons.",
        "Losowy punkt odniesienia: obie strony wybierają losowe ruchy.": "Random baseline: both sides choose random moves.",
        "Stałe przeszukiwanie kontra losowe ruchy.": "Fixed search against random moves.",
        "Bot adaptacyjny kontra losowy punkt odniesienia.": "Adaptive bot against the random baseline.",
        "Bot adaptacyjny kontra bot ze stałą oceną.": "Adaptive bot against a bot with fixed evaluation.",
        "Badanie uczenia z Twoich partii rozpoczniesz w Kampanii badawczej.": "Start a Research campaign to study learning from your games.",
        "Zakończenie i zapis": "Finish and save",
        "Raport prezentuje do 200 wierszy; pełne dane są dostępne w plikach technicznych.": "Reports show up to 200 rows; full data is available in technical files.",
        "Liczba półruchów przewidywanych w przeszukiwaniu. Większa głębokość wydłuża obliczenia; budżet węzłów może zakończyć je wcześniej.": "Number of individual moves searched ahead. Greater depth takes longer; the node budget may end the search earlier.",
        "Budżet odwiedzonych pozycji na jeden ruch agenta. Wspólny limit pomaga porównywać metody przy tym samym budżecie obliczeń.": "Budget of visited positions per agent move. A shared limit helps compare methods with the same computation budget.",
        "Ziarno generatora losowego. Zachowaj tę samą wartość i konfigurację, aby odtworzyć warunki badania; samo ziarno nie gwarantuje identycznego czasu wykonania.": "Random generator seed. Keep the same value and configuration to reproduce research conditions; the seed alone does not guarantee identical running time.",
        "Liczba partii treningowych człowieka z każdą metodą. Cztery metody oznaczają łącznie 4 \u00d7 tę wartość. Ocena i turniej to dodatkowe gry.": "Human training games per method. Four methods mean 4 \u00d7 this value in total. Evaluation and tournament games are additional.",
        "Stan modelu po danej liczbie partii treningowych. 0 oznacza stan przed nauką. Wybierz istniejący checkpoint; ocena nie aktualizuje modelu.": "Model state after this many training games. 0 is the state before learning. Select an existing checkpoint; evaluation does not update the model.",
        "Adaptive: buduje profil ruchów przeciwnika i używa go do korekty wyboru ruchów.": "Adaptive: builds an opponent move profile and uses it to adjust move selection.",
        "Imitation: uczy ranking legalnych ruchów na podstawie ruchów człowieka. Naśladuje wybory, nie oceny silnika.": "Imitation: learns a ranking of legal moves from human moves. It imitates choices, not engine evaluations.",
        "TD: aktualizuje ocenę pozycji na podstawie kolejnych pozycji i wyniku partii (temporal difference).": "TD: updates position evaluation from successive positions and game results (temporal difference).",
        "Static: punkt odniesienia ze stałą oceną pozycji. Nie uczy się podczas kampanii.": "Static: a baseline with fixed position evaluation. It does not learn during the campaign.",
        "Ocena porównuje zapisane checkpointy bez dalszej nauki. Turniej zestawia zamrożonych agentów. Gry obejmują pary kolorów; wyniki nie zmieniają treningu.": "Evaluation compares saved checkpoints without further learning. The tournament pairs frozen agents. Games include both colors; results do not change training.",
        "Grasz z wybraną metodą i istniejącym checkpointem bez aktualizacji modelu. Najpierw dokończ aktywną partię.": "Play against the selected method and an existing checkpoint without updating the model. Finish the active game first.",
        "Jeden półruch to ruch jednej strony. 200 półruchów to do 100 pełnych ruchów. Partia przerwana limitem nie jest automatycznie remisem.": "One half-move is one move by one side. 200 half-moves allow up to 100 full moves. Reaching the limit does not automatically mean a draw.",
        "Ruchy w notacji UCI, np. e2e4 e7e5. Oddziel otwarcia średnikiem. Pusty fragment oznacza pozycję początkową. Zachowaj zestaw przy porównywaniu badań.": "UCI moves, e.g. e2e4 e7e5. Separate openings with semicolons. An empty segment means the initial position. Keep the same set when comparing studies.",
        "CSV zawiera tabele do dalszej analizy, JSON dane i konfigurację, PGN zapis partii. Plik SQLite przechowuje kampanię potrzebną do wznowienia.": "CSV contains tables for analysis, JSON data and configuration, PGN game moves. SQLite stores the campaign needed to resume.",
        "Wyniki dotyczą wczytanego folderu. Sprawdź liczbę partii, checkpoint, pary kolorów i przerwania limitem przed porównaniem metod. Przewaga materiału nie jest wynikiem partii.": "Results cover the loaded folder. Check game count, checkpoint, color pairs and move-limit stops before comparing methods. Material advantage is not a game result.",
        "Liczba gier w wybranym porównaniu. Pełny zestaw uruchamia cztery porównania, każde z taką liczbą gier.": "Games in the selected comparison. The full suite runs four comparisons, each with this many games.",
        "FEN opisuje pozycję, stronę na ruchu, roszady i liczniki. Służy do odtwarzania pozycji; nie zawiera pełnej historii partii.": "FEN describes the position, side to move, castling rights and counters. It can restore a position but does not contain the full move history.",
    }
)


EN.update(
    {
        "Pseudonim uczestnika": "Participant nickname",
        "Wybrano figurę na polu {square}.": "Selected the piece on {square}.",
        "{agent} • Grasz {color}. {move}{turn}": "{agent} • You play {color}. {move}{turn}",
        "białymi": "white",
        "czarnymi": "black",
        "białe": "white",
        "czarne": "black",
        "Ty": "You",
        "gracz": "you",
        "bot": "bot",
        "{reason}. Wynik zapisany. Obejrzyj ostatnią pozycję.": "{reason}. Result saved. Review the final position.",
        " Trening ukończony — otwórz Ocenę i raport.": " Training complete — open Evaluation and report.",
        "Wczytano raporty: {count} plików.": "Loaded reports: {count} files.",
        "Folder nie istnieje: {folder}": "Folder does not exist: {folder}",
        "Wygrana białych": "White wins",
        "Wygrana czarnych": "Black wins",
        "Partia bez rozstrzygnięcia": "Unfinished game",
        "Równy materiał": "Equal material",
        "Gracz poddał partię.": "Player resigned.",
        "Hetman": "Queen",
        "Wieża": "Rook",
        "Goniec": "Bishop",
        "Skoczek": "Knight",
        "Promocja": "Promotion",
        "Wybierz figurę": "Choose a piece",
        "Ocena zakończona. Raport zapisany obok kampanii.": "Evaluation complete. Report saved beside the campaign.",
        "Turniej zamrożonych agentów. Zapis po każdej partii.": "Frozen-agent tournament. Saved after every game.",
        "Raport badania": "Research report",
    }
)


EN.update(
    {
        "Agent": "Agent",
        "Na ruchu białe.": "White to move.",
        "Na ruchu czarne.": "Black to move.",
        "Na ruchu białe. Szach.": "White to move. Check.",
        "Na ruchu czarne. Szach.": "Black to move. Check.",
        "Mat. Wygrywają białe.": "Checkmate. Winner: White.",
        "Mat. Wygrywają czarne.": "Checkmate. Winner: Black.",
        "Remis przez pat.": "Draw by stalemate.",
        "Remis: niewystarczający materiał.": "Draw by insufficient material.",
        "Koniec partii. Wynik: {result}.": "Game over. Result: {result}.",
        "Białe +{value}": "White +{value}",
        "Czarne +{value}": "Black +{value}",
    }
)


EN.update(
    {
        "Uruchamiaj na pełnym ekranie": "Start in fullscreen",
        "F11 przełącza pełny ekran, Esc wraca do okna.": "F11 toggles fullscreen, Esc returns to the window.",
    }
)


def set_language(language: str) -> None:
    global _language
    _language = language if language in ("pl", "en") else "pl"


def tr(text: str) -> str:
    if _language == "pl":
        return text
    if text in EN:
        return EN[text]
    return text


def _caption(widget: QWidget, key: str, current: str) -> str:
    previous = widget.property(key)
    reverse = {value: source for source, value in EN.items()}
    source = (
        previous[0]
        if previous and current == previous[1]
        else reverse.get(current, current)
    )
    rendered = tr(source)
    widget.setProperty(key, [source, rendered])
    return rendered


def localize(root: QWidget) -> None:
    """Translate widget captions in place, preserving data and selections."""
    for widget in [root, *root.findChildren(QWidget)]:
        help_source = widget.property("help_source")
        if help_source:
            widget.setToolTip("<p>" + escape(tr(help_source)) + "</p>")
        elif widget.toolTip():
            widget.setToolTip(_caption(widget, "tooltip_pair", widget.toolTip()))
        for key, getter, setter in (
            ("accessible_name_pair", widget.accessibleName, widget.setAccessibleName),
            (
                "accessible_description_pair",
                widget.accessibleDescription,
                widget.setAccessibleDescription,
            ),
        ):
            if getter():
                setter(_caption(widget, key, getter()))
        if isinstance(widget, (QLineEdit, QPlainTextEdit, QTextEdit)):
            widget.setPlaceholderText(
                _caption(widget, "placeholder_pair", widget.placeholderText())
            )
        if isinstance(widget, (QLabel, QAbstractButton)):
            widget.setText(_caption(widget, "translation_pair", widget.text()))
        if isinstance(widget, (QComboBox, QTabWidget)):
            for index in range(widget.count()):
                current = (
                    widget.itemText(index)
                    if isinstance(widget, QComboBox)
                    else widget.tabText(index)
                )
                rendered = _caption(widget, f"translation_{index}", current)
                if isinstance(widget, QComboBox):
                    widget.setItemText(index, rendered)
                else:
                    widget.setTabText(index, rendered)

    for widget in [root, *root.findChildren(QWidget)]:
        refresh = getattr(widget, "refresh_translation", None)
        if callable(refresh):
            refresh()


def game_status(text: str) -> str:
    """Localize the backend's status without changing its protocol or output."""
    reverse = {value: source for source, value in EN.items()}
    if text.startswith("Game over. Result: "):
        result = text.removeprefix("Game over. Result: ").removesuffix(".")
        return tr("Koniec partii. Wynik: {result}.").format(result=result)
    return tr(reverse.get(text, text))


EN.update(
    {
        "Przewidywanie przeciwnika": "Opponent lookahead",
        "1 — Szybkie": "1 — Fast",
        "2 — Umiarkowane": "2 — Moderate",
        "3 — Dokładne": "3 — Detailed",
        "4 — Najgłębsze": "4 — Deepest",
        "RandomBot wybiera losowe legalne ruchy. "
        "Poziom przewidywania nie wpływa na jego grę.": "RandomBot picks random legal moves. Lookahead has no effect on its play.",
        "Zakres 1-4: tyle półruchów bot analizuje w przód. "
        "1 jest najszybsze, 4 analizuje najgłębiej i może długo liczyć. "
        "Większa głębokość zwykle pomaga, ale nie gwarantuje wygranej. "
        "To nie jest ranking Elo.": "Range 1-4: the number of half-moves the bot looks ahead. "
        "1 is fastest; 4 searches deepest and may take a long time. "
        "Greater depth usually helps but does not guarantee a win. This is not an Elo rating.",
        "Końcowa pozycja": "Final position",
        "Pomoc dotycząca parametru": "Parameter help",
        "Mat: zaznaczony król jest szachowany. Legalne odpowiedzi: 0. "
        "Nie można uciec królem, zbić szachującej figury ani zasłonić szacha.": "Checkmate: the highlighted king is in check. Legal replies: 0. "
        "There is no king escape, capture of the checking piece, or way to block the check.",
        "Pat: król nie jest szachowany, ale strona na ruchu nie ma legalnego ruchu. To remis.": "Stalemate: the king is not in check, but the side to move has no legal move. A draw.",
        "Końcowa pozycja do obejrzenia. Powód zakończenia podano przy wyniku.": "Final position for inspection. The reason the game ended is shown beside the result.",
    }
)


EN.update(
    {
        "? Pomoc": "? Help",
        "← Powrót do menu": "← Back to menu",
        "Na żywo": "Live",
        "Poprzedni ruch": "Previous move",
        "Następny ruch": "Next move",
        "Półruch": "Half-move",
        "Bilans białych": "White material balance",
        "Partie i ruchy AI": "Games and AI moves",
        "Rzeczywiste wyniki partii": "Actual game results",
        "Rozpocznij porównanie, aby śledzić ruchy AI.": "Start a comparison to follow AI moves.",
        "Ruchy: K król, Q hetman, R wieża, B goniec, N skoczek. "
        "Duże litery na planszy = białe. Bilans materiału nie jest oceną błędu.": "Moves: K king, Q queen, R rook, B bishop, N knight. "
        "Uppercase board pieces are white. Material balance is not a blunder assessment.",
    }
)

EN.update(
    {
        "← Ruch": "← Move",
        "Ruch →": "Move →",
        "Ostatni ruch": "Last move",
        "Podgląd zachowuje ostatnie 100 partii tego uruchomienia.": "The viewer retains the last 100 games from this run.",
    }
)

EN.update(
    {
        "Liczba partii na jedno ustawienie kolorów. Różne boty zamieniają "
        "kolory, więc grają 2 \u00d7 tę liczbę. Losowy z losowym: 1 \u00d7. "
        "Pełny zestaw: 7 \u00d7. Więcej partii wydłuża porównanie i daje "
        "więcej danych; kilka gier nie wystarcza do oceny skuteczności.": "Games per color assignment. Different bots swap colors, playing 2 times "
        "this count. Random vs random: 1 time. Full suite: 7 times. "
        "More games take longer and provide more data; a few games are not enough to assess effectiveness.",
    }
)

EN.update({
    "Powiększ wykres": "Enlarge chart",
    "Podgląd wykresu": "Chart preview",
    "Dopasuj do okna": "Fit to window",
    "Zamknij": "Close",
})

EN.update({
    "Partia zakończona. Wczytaj zapis, aby odświeżyć wynik.": "Game over. Reload the saved campaign to refresh the result.",
})

EN.update({
    "Nie wybrano zapisu kampanii.": "No campaign save selected.",
    "Plik kampanii: {path}": "Campaign file: {path}",
    "Nie udało się otworzyć lub wznowić kampanii": "Could not open or resume the campaign",
    "Wczytaj ponownie tę kampanię": "Reload this campaign",
    "Wybierz inny zapis…": "Choose another save…",
    "Szczegóły błędu": "Error details",
    "Wróć do wyboru kampanii": "Back to campaign selection",
    "Nie udało się wznowić kampanii.": "Could not resume the campaign.",
    "Wczytano zapis. Wznów partię.": "Save loaded. Resume the game.",
    "Wznów zapisaną partię": "Resume saved game",
    "Ten zapis wymaga zgodnej wersji aplikacji. Zamknij program i uruchom "
    "wersję obsługującą ten zapis. Potem kliknij "
    "„Wczytaj ponownie tę kampanię”. "
    "Samo ponawianie w tej wersji nie usunie błędu.":
        "This save requires a compatible app version. Close the app and run a version "
        "that supports this save, then click Reload this campaign. Retrying in this version will not fix the error.",
    "Nie można teraz kontynuować kampanii. Kliknij „Wczytaj ponownie tę "
    "kampanię”, aby spróbować z tego samego pliku, albo „Wybierz inny zapis…”.":
        "The campaign cannot continue right now. Click Reload this campaign to retry "
        "from the same file, or Choose another save.",
})

EN.update({
    "Wczytywanie partii… Poczekaj na odtworzenie ruchów.": "Loading game… Please wait while saved moves are restored.",
})

EN.update({
    "Poprzedni zapis zachowano w: {path}": "Previous save backed up to: {path}",
})
