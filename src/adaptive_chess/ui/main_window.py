from PySide6.QtCore import QProcess
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QScrollArea,
    QStackedWidget,
    QWidget,
)

from adaptive_chess.play.human_vs_bot_session import HumanVsBotGameSummary
from adaptive_chess.ui.app_settings import (
    AppSettings,
    AppSettingsStore,
)
from adaptive_chess.ui.navigation import ScreenName
from adaptive_chess.ui.screens.campaign_screen import CampaignScreen
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
        available = self.screen().availableGeometry()
        self.resize(min(1180, available.width()), min(760, available.height() - 40))
        self._fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self._fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        self._escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        self._escape_shortcut.activated.connect(self.leave_fullscreen)

        self._stack = QStackedWidget()
        self._screens: dict[ScreenName, int] = {}

        self._game_screen: GameScreen | None = None
        self._game_summary_screen: GameSummaryScreen | None = None
        self._settings_store = AppSettingsStore()
        self._experiments_screen: ExperimentsScreen | None = None

        self._build_screens()

        self.setCentralWidget(self._stack)
        self.show_screen(ScreenName.MENU)

    def show_startup(self) -> None:
        if self._settings_store.load().fullscreen:
            self.showFullScreen()
        else:
            self.show()

    def toggle_fullscreen(self) -> None:
        self.showMaximized() if self.isFullScreen() else self.showFullScreen()

    def leave_fullscreen(self) -> None:
        if self._campaign_screen._dashboard.busy:
            self._campaign_screen._dashboard.cancel()
            return
        if (
            self._campaign_screen._process is not None
            and self._campaign_screen._process.state()
            != QProcess.ProcessState.NotRunning
        ):
            self._campaign_screen.stop_tournament()
            return
        if self.isFullScreen():
            self.showMaximized()

    def _apply_settings(self, settings: AppSettings) -> None:
        from adaptive_chess.ui.i18n import localize, set_language
        from adaptive_chess.ui.theme import (
            DARK_THEME_STYLESHEET,
            LIGHT_THEME_STYLESHEET,
            apply_palette,
        )

        set_language(settings.language)
        localize(self._stack)
        app = QApplication.instance()
        if isinstance(app, QApplication):
            apply_palette(app, settings.theme)
            stylesheet = (
                LIGHT_THEME_STYLESHEET
                if settings.theme == "light"
                else DARK_THEME_STYLESHEET
            )
            if app.styleSheet() != stylesheet:
                app.setStyleSheet(stylesheet)
        self._campaign_screen._reply_timer.setInterval(settings.bot_delay_ms)
        if self.isVisible():
            self.showFullScreen() if settings.fullscreen else self.showMaximized()

        if self._game_screen is not None:
            self._game_screen.apply_defaults(
                bot_kind=settings.default_bot,
                human_color=settings.default_human_color,
                depth=settings.default_depth,
            )

        if self._experiments_screen is not None:
            self._experiments_screen.set_default_output_dir(
                settings.default_experiment_output_dir
            )

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

    def start_campaign_flow(self) -> None:
        self._campaign_screen.show_entry()
        self.show_screen(ScreenName.CAMPAIGN)

    def _build_screens(self) -> None:
        menu_screen = MenuScreen(
            on_play_clicked=self.start_new_game_flow,
            on_experiments_clicked=lambda: self.show_screen(ScreenName.EXPERIMENTS),
            on_results_clicked=lambda: self.show_screen(ScreenName.RESULTS),
            on_settings_clicked=lambda: self.show_screen(ScreenName.SETTINGS),
            on_exit_clicked=self._close_window,
            on_campaign_clicked=self.start_campaign_flow,
        )

        self._game_screen = GameScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
            on_game_finished=self.show_game_summary,
        )

        self._game_summary_screen = GameSummaryScreen(
            on_play_again_clicked=self.start_new_game_flow,
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        self._experiments_screen = ExperimentsScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        results_screen = ResultsScreen(
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
        )

        settings_screen = SettingsScreen(
            settings_store=self._settings_store,
            on_back_to_menu_clicked=lambda: self.show_screen(ScreenName.MENU),
            on_settings_saved=self._apply_settings,
        )

        self._add_screen(ScreenName.MENU, menu_screen)
        self._add_screen(ScreenName.GAME, self._game_screen)
        self._add_screen(ScreenName.GAME_SUMMARY, self._game_summary_screen)
        self._add_screen(
            ScreenName.EXPERIMENTS,
            self._experiments_screen,
        )
        self._add_screen(ScreenName.RESULTS, results_screen)
        self._add_screen(ScreenName.SETTINGS, settings_screen)
        self._campaign_screen = CampaignScreen(
            on_back=lambda: self.show_screen(ScreenName.MENU)
        )
        # One window-wide Escape binding avoids Qt's ambiguous-shortcut handling.
        self._campaign_screen._dashboard.escape.setEnabled(False)
        self._add_screen(ScreenName.CAMPAIGN, self._campaign_screen)
        self._apply_settings(self._settings_store.load())

    def closeEvent(self, event) -> None:
        self._campaign_screen._dashboard.cancel()
        if self._campaign_screen.thinking or (
            self._game_screen is not None and self._game_screen.thinking
        ):
            self.statusBar().showMessage("Poczekaj na zakończenie ruchu i zapisu.")
            event.ignore()
            return
        self._campaign_screen.stop_tournament()
        super().closeEvent(event)

    def _close_window(self) -> None:
        self.close()

    def _add_screen(
        self,
        screen_name: ScreenName,
        widget: QWidget,
    ) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        index = self._stack.addWidget(scroll)
        self._screens[screen_name] = index
