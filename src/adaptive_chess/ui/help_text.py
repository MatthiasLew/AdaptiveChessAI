"""Contextual help, kept separate from research behavior."""

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QWidget

from adaptive_chess.ui.i18n import tr

HELP = {
    "depth": (
        "Liczba półruchów przewidywanych w przeszukiwaniu. Większa "
        "głębokość wydłuża obliczenia; budżet węzłów może zakończyć je "
        "wcześniej."
    ),
    "nodes": (
        "Budżet odwiedzonych pozycji na jeden ruch agenta. Wspólny limit "
        "pomaga porównywać metody przy tym samym budżecie obliczeń."
    ),
    "seed": (
        "Ziarno generatora losowego. Zachowaj tę samą wartość i "
        "konfigurację, aby odtworzyć warunki badania; samo ziarno nie "
        "gwarantuje identycznego czasu wykonania."
    ),
    "games": (
        "Liczba partii treningowych człowieka z każdą metodą. Cztery metody "
        "oznaczają łącznie 4 \u00d7 tę wartość. Ocena i turniej to dodatkowe "
        "gry."
    ),
    "checkpoint": (
        "Stan modelu po danej liczbie partii treningowych. 0 oznacza stan "
        "przed nauką. Wybierz istniejący checkpoint; ocena nie aktualizuje "
        "modelu."
    ),
    "adaptive": (
        "Adaptive: buduje profil ruchów przeciwnika i używa go do korekty "
        "wyboru ruchów."
    ),
    "imitation": (
        "Imitation: uczy ranking legalnych ruchów na podstawie ruchów "
        "człowieka. Naśladuje wybory, nie oceny silnika."
    ),
    "td": (
        "TD: aktualizuje ocenę pozycji na podstawie kolejnych pozycji i "
        "wyniku partii (temporal difference)."
    ),
    "static": (
        "Static: punkt odniesienia ze stałą oceną pozycji. Nie uczy się "
        "podczas kampanii."
    ),
    "evaluation": (
        "Ocena porównuje zapisane checkpointy bez dalszej nauki. Turniej "
        "zestawia zamrożonych agentów. Gry obejmują pary kolorów; wyniki "
        "nie zmieniają treningu."
    ),
    "control": (
        "Grasz z wybraną metodą i istniejącym checkpointem bez aktualizacji "
        "modelu. Najpierw dokończ aktywną partię."
    ),
    "limit": (
        "Jeden półruch to ruch jednej strony. 200 półruchów to do 100 "
        "pełnych ruchów. Partia przerwana limitem nie jest automatycznie "
        "remisem."
    ),
    "openings": (
        "Ruchy w notacji UCI, np. e2e4 e7e5. Oddziel otwarcia średnikiem. "
        "Pusty fragment oznacza pozycję początkową. Zachowaj zestaw przy "
        "porównywaniu badań."
    ),
    "files": (
        "CSV zawiera tabele do dalszej analizy, JSON dane i konfigurację, "
        "PGN zapis partii. Plik SQLite przechowuje kampanię potrzebną do "
        "wznowienia."
    ),
    "reports": (
        "Wyniki dotyczą wczytanego folderu. Sprawdź liczbę partii, "
        "checkpoint, pary kolorów i przerwania limitem przed porównaniem "
        "metod. Przewaga materiału nie jest wynikiem partii."
    ),
    "matches": (
        "Liczba partii na jedno ustawienie kolorów. Różne boty zamieniają "
        "kolory, więc grają 2 \u00d7 tę liczbę. Losowy z losowym: 1 \u00d7. "
        "Pełny zestaw: 7 \u00d7. Więcej partii wydłuża porównanie i daje "
        "więcej danych; kilka gier nie wystarcza do oceny skuteczności."
    ),
    "fen": (
        "FEN opisuje pozycję, stronę na ruchu, roszady i liczniki. Służy do "
        "odtwarzania pozycji; nie zawiera pełnej historii partii."
    ),
}


def help_for(widget: QWidget, key: str) -> None:
    # Rich text allows Qt to wrap long help instead of spanning the desktop.
    source = HELP[key]
    widget.setProperty("help_source", source)
    widget.setToolTip("<p>" + escape(tr(source)) + "</p>")


def method_help(combo: QComboBox) -> None:
    for index in range(combo.count()):
        key = str(combo.itemData(index) or combo.itemText(index)).lower()
        if key in HELP:
            combo.setItemData(index, tr(HELP[key]), Qt.ItemDataRole.ToolTipRole)
    key = str(combo.currentData() or combo.currentText()).lower()
    if key in HELP:
        help_for(combo, key)
