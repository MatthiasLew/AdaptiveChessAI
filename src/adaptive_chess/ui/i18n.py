"""Local interface catalogue. User data and raw exports are never translated."""

from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel, QTabWidget, QWidget

_language = "pl"
EN = {
    "Brak zakończonej partii.": "No finished game yet.",
    "Graj ponownie": "Play again", "Zapisz partię": "Save game",
    "Końcowy FEN": "Final FEN", "Końcowy materiał": "Final material balance",
    "Liczba półruchów": "Individual moves", "Podsumowanie partii": "Game summary",
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
    "Ocena i raport": "Evaluation and report",
    "Limit półruchów": "Maximum individual moves",
    "Agent kontrolny": "Evaluation agent",
    "Checkpoint": "Saved model",
    "Oceń checkpointy / turniej": "Evaluate models / tournament",
    "Partia kontrolna (bez nauki)": "Evaluation game (learning disabled)",
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
