import sys

from PySide6.QtWidgets import QApplication

from adaptive_chess.ui.main_window import MainWindow
from adaptive_chess.ui.theme import DARK_THEME_STYLESHEET


def run_gui() -> int:
    """
    Uruchamia aplikację GUI.

    Returns:
        Kod zakończenia aplikacji.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("AdaptiveChessAI")
    app.setStyleSheet(DARK_THEME_STYLESHEET)

    window = MainWindow()
    window.show_startup()

    return app.exec()


def main() -> None:
    raise SystemExit(run_gui())


if __name__ == "__main__":
    main()
