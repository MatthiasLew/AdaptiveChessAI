from PySide6.QtWidgets import QMainWindow, QStackedWidget

from adaptive_chess.play.human_vs_bot_session import HumanVsBotGameSummary
from adaptive_chess.ui.navigation import ScreenName
from adaptive_chess.ui.screens.experiments_screen import ExperimentsScreen
from adaptive_chess.ui.screens.game_screen import GameScreen
from adaptive_chess.ui.screens.game_summary_screen import GameSummaryScreen
from adaptive_chess.ui.screens.menu_screen import MenuScreen
from adaptive_chess.ui.screens.results_screen import ResultsScreen
from adaptive_chess.ui.screens.settings_screen import SettingsScreen


class MainWindow(QMainWindow):
    """
    Główne okno aplikacji AdaptiveChessAI.

    Odpowiada za przełączanie ekranów.
    Logika gry jest obsługiwana przez GameScreen i HumanVsBotSession.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("AdaptiveChessAI")
        self.resize(1180, 760)

        self._stack = QStackedWidget()
        self._screens: dict[ScreenName, int] = {}

        self._game_screen: GameScreen | None = None
        self._game_summary_screen: GameSummaryScreen | None = None

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

    def show_game_summary(self, summary: HumanVsBotGameSummary) -> None:
        """
        Pokazuje ekran podsumowania partii.
        """
        if self._game_summary_screen is None:
            raise RuntimeError("Game summary screen is not initialized.")

        self._game_summary_screen.set_summary(summary)
        self.show_screen(ScreenName.GAME_SUMMARY)

    def start_new_game_flow(self) -> None:
        """
        Przygotowuje ekran gry do nowej partii i przełącza na niego widok.
        """
        if self._game_screen is None:
            raise RuntimeError("Game screen is not initialized.")

        self._game_screen.prepare_for_new_game()
        self.show_screen(ScreenName.GAME)

    def _build_screens(self) -> None:
        menu_screen = MenuScreen(
            on_play_clicked=self.start_new_game_flow,
            on_experiments_clicked=lambda: self.show_screen(ScreenName.EXPERIMENTS),
            on_results_clicked=lambda: self.show_screen(ScreenName.RESULTS),
            on_settings_clicked=lambda: self.show_screen(ScreenName.SETTINGS),
            on_exit_clicked=self.close,
        )

        self._game_screen = GameScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
            on_game_finished=self.show_game_summary,
        )

        self._game_summary_screen = GameSummaryScreen(
            on_play_again_clicked=self.start_new_game_flow,
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
        self._add_screen(ScreenName.GAME, self._game_screen)
        self._add_screen(ScreenName.GAME_SUMMARY, self._game_summary_screen)
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