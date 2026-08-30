from PySide6.QtWidgets import QMainWindow, QStackedWidget

from adaptive_chess.ui.navigation import ScreenName
from adaptive_chess.ui.screens.experiments_screen import ExperimentsScreen
from adaptive_chess.ui.screens.game_screen import GameScreen
from adaptive_chess.ui.screens.menu_screen import MenuScreen
from adaptive_chess.ui.screens.results_screen import ResultsScreen
from adaptive_chess.ui.screens.settings_screen import SettingsScreen


class MainWindow(QMainWindow):
    """
    Główne okno aplikacji AdaptiveChessAI.

    Odpowiada za przełączanie ekranów.
    Logika gry będzie podpięta do osobnych widoków, nie bezpośrednio tutaj.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("AdaptiveChessAI")
        self.resize(1180, 760)

        self._stack = QStackedWidget()
        self._screens: dict[ScreenName, int] = {}

        self._build_screens()

        self.setCentralWidget(self._stack)
        self.show_screen(ScreenName.MENU)

    def show_screen(self, screen_name: ScreenName) -> None:
        """
        Przełącza aktywny ekran aplikacji.
        """
        if screen_name not in self._screens:
            raise ValueError(f"Unknown screen: {screen_name}")

        self._stack.setCurrentIndex(self._screens[screen_name])

    def _build_screens(self) -> None:
        menu_screen = MenuScreen(
            on_play_clicked=lambda: self.show_screen(ScreenName.GAME),
            on_experiments_clicked=lambda: self.show_screen(ScreenName.EXPERIMENTS),
            on_results_clicked=lambda: self.show_screen(ScreenName.RESULTS),
            on_settings_clicked=lambda: self.show_screen(ScreenName.SETTINGS),
            on_exit_clicked=self.close,
        )

        game_screen = GameScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        experiments_screen = ExperimentsScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        results_screen = ResultsScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        settings_screen = SettingsScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        self._add_screen(ScreenName.MENU, menu_screen)
        self._add_screen(ScreenName.GAME, game_screen)
        self._add_screen(ScreenName.EXPERIMENTS, experiments_screen)
        self._add_screen(ScreenName.RESULTS, results_screen)
        self._add_screen(ScreenName.SETTINGS, settings_screen)

    def _add_screen(
        self,
        screen_name: ScreenName,
        widget,
    ) -> None:
        index = self._stack.addWidget(widget)
        self._screens[screen_name] = index