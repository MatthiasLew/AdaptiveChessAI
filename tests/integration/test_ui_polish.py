"""Behavioral regression checks for presentation and compact layouts."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QScrollArea, QSpinBox

from adaptive_chess.ui.app_settings import AppSettings, AppSettingsStore
from adaptive_chess.ui.help_text import HELP, help_for
from adaptive_chess.ui.i18n import EN, game_status, localize, set_language
from adaptive_chess.ui.main_window import MainWindow
from adaptive_chess.ui.navigation import ScreenName
from adaptive_chess.ui.screens.campaign_screen import CampaignScreen
from adaptive_chess.ui.screens.results_screen import ResultsScreen
from adaptive_chess.ui.theme import DARK, LIGHT, build_stylesheet
from adaptive_chess.ui.widgets.components import ActionCard, Disclosure


@pytest.fixture
def app():
    application = QApplication.instance() or QApplication([])
    set_language("pl")
    yield application
    set_language("pl")


@pytest.mark.parametrize(
    "fen,expected",
    [
        ("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3", "Mat:"),
        ("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1", "Pat:"),
        (chess.STARTING_FEN, "Końcowa pozycja"),
    ],
)
def test_summary_retains_final_position_without_changing_it(app, fen, expected):
    from adaptive_chess.play.human_vs_bot_session import HumanVsBotGameSummary
    from adaptive_chess.ui.screens.game_summary_screen import GameSummaryScreen

    summary = HumanVsBotGameSummary(
        "RandomBot",
        chess.BLACK,
        chess.WHITE,
        "0-1",
        "Koniec partii",
        fen,
        4,
        0,
        (),
    )
    screen = GameSummaryScreen(lambda: None, lambda: None)
    screen.set_summary(summary)
    assert screen._board_widget._board.fen() == fen
    assert screen._board_widget._flipped
    assert expected in screen._position_help.text()
    screen._board_widget.square_clicked.emit(chess.E1)
    assert screen._board_widget._board.fen() == fen
    for language in ("en", "pl"):
        set_language(language)
        localize(screen)
        if expected == "Mat:":
            assert (
                "Legal replies: 0" if language == "en" else "Legalne odpowiedzi: 0"
            ) in screen._position_help.text()
    screen.close()


def test_strength_choices_persist_depth_and_explain_random(app, monkeypatch):
    from adaptive_chess.ui.screens.settings_screen import SettingsScreen

    saved = []
    monkeypatch.setattr(AppSettingsStore, "load", lambda self: AppSettings())
    monkeypatch.setattr(
        AppSettingsStore, "save", lambda self, value: saved.append(value)
    )
    screen = SettingsScreen(AppSettingsStore(), lambda: None, lambda value: None)
    assert not screen._depth_combo.isEditable()
    assert not screen._depth_combo.isEnabled()
    assert "RandomBot" in screen._strength_help.text()
    screen._bot_combo.setCurrentIndex(1)
    assert screen._depth_combo.isEnabled()
    assert "1-4" in screen._strength_help.text()
    for index in range(4):
        screen._depth_combo.setCurrentIndex(index)
        screen._save_settings()
        assert saved[-1].default_depth == index + 1
    set_language("en")
    localize(screen)
    assert "Deepest" in screen._depth_combo.currentText()
    assert "half-moves" in screen._strength_help.text()
    screen.close()


def test_exported_position_last_move_is_display_only(app):
    from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget

    board = chess.Board()
    board.push_uci("e2e4")
    exported = chess.Board(board.fen())
    widget = ChessBoardWidget()
    widget.set_board(exported, last_move=board.peek())
    assert widget._last_move == chess.Move.from_uci("e2e4")
    assert not exported.move_stack
    assert widget._board.fen() == exported.fen()
    widget.set_board(chess.Board())
    assert widget._last_move is None


def test_parameter_help_opens_from_keyboard_and_retranslates(app, monkeypatch):
    from PySide6.QtWidgets import QToolTip

    from adaptive_chess.ui.widgets.components import HelpButton

    shown = []
    monkeypatch.setattr(QToolTip, "showText", lambda *args: shown.append(args[1]))
    button = HelpButton("depth")
    button.show()
    button.setFocus()
    QTest.keyClick(button, Qt.Key.Key_Space)
    assert "półruchów" in shown[-1]
    set_language("en")
    localize(button)
    QTest.keyClick(button, Qt.Key.Key_Space)
    assert shown[-1] != shown[0]
    assert button.accessibleName() == "Parameter help"
    button.close()


def test_help_and_placeholder_round_trip_preserves_user_input(app):
    field = QLineEdit("Wygląd")  # User content must never be translated.
    field.setPlaceholderText("Pseudonim uczestnika")
    help_for(field, "seed")
    for language, expected in (("en", "Random generator"), ("pl", "Ziarno")):
        set_language(language)
        localize(field)
        assert expected in field.toolTip()
        assert field.text() == "Wygląd"
    assert field.placeholderText() == "Pseudonim uczestnika"
    assert all(source in EN for source in HELP.values())


def test_campaign_summary_and_method_help_retranslate_without_reset(app):
    screen = CampaignScreen(lambda: None)
    try:
        screen._games.setValue(7)
        screen._nodes.setValue(123)
        screen._participant.setText("Wygląd")
        screen._eval_agent.setCurrentIndex(2)
        for language, expected in (
            ("en", "28 training games"),
            ("pl", "28 partii treningowych"),
        ):
            set_language(language)
            localize(screen)
            assert expected in screen._configuration_summary.text()
            assert "123" in screen._budget_summary.text()
            assert screen._participant.text() == "Wygląd"
            assert screen._eval_agent.currentText() == "td"
            assert "TD:" in screen._eval_agent.toolTip()
            for index in range(screen._eval_agent.count()):
                assert screen._eval_agent.itemData(index, Qt.ItemDataRole.ToolTipRole)
    finally:
        screen.close()


def test_disclosure_preserves_values_and_is_keyboard_operable(app):
    value = QSpinBox()
    value.setValue(42)
    details = Disclosure("Parametry zaawansowane", value)
    details.show()
    try:
        assert not value.isVisible()
        details.toggle.setFocus()
        QTest.keyClick(details.toggle, Qt.Key.Key_Space)
        assert value.isVisible() and value.value() == 42
        QTest.keyClick(details.toggle, Qt.Key.Key_Space)
        assert not value.isVisible() and value.value() == 42
    finally:
        details.close()


def test_action_card_mouse_and_keyboard_navigation(app):
    calls = []
    card = ActionCard("Kampania badawcza", "Plan kampanii", lambda: calls.append(1))
    card.resize(500, 150)
    card.show()
    try:
        app.processEvents()
        QTest.mouseClick(card, Qt.MouseButton.LeftButton, pos=card.rect().center())
        card.setFocus()
        QTest.keyClick(card, Qt.Key.Key_Space)
        assert calls == [1, 1]
        set_language("en")
        localize(card)
        assert card.accessibleName() == "Research campaign"
        assert any(c.text() == "Research campaign" for c in card.findChildren(QLabel))
    finally:
        card.close()


def test_dashboard_counts_unfinished_separately_and_clears_stale_data(app, tmp_path):
    (tmp_path / "games.csv").write_text(
        "result,reached_move_limit\n1-0,False\n0-1,False\n1/2-1/2,False\n*,True\n",
        encoding="utf-8",
    )
    screen = ResultsScreen(lambda: None)
    try:
        screen._folder_edit.setText(str(tmp_path))
        screen._load_results_folder()
        assert [card.value.text() for card in screen._stats] == ["4", "1", "1", "1"]
        assert [bar.value() for bar in screen._bars] == [1, 1, 1, 1]
        assert not screen._reports_disclosure.toggle.isChecked()
        set_language("en")
        localize(screen)
        assert "White wins" in screen._overview.toPlainText()
        screen._folder_edit.setText(str(tmp_path / "missing"))
        screen._load_results_folder()
        assert all(card.value.text() == "—" for card in screen._stats)
        assert not screen._overview.toPlainText()
    finally:
        screen.close()


@pytest.mark.parametrize("theme", ["dark", "light"])
@pytest.mark.parametrize("language", ["pl", "en"])
@pytest.mark.parametrize("size", [(1366, 704), (910, 469)])
def test_screens_fit_logical_width_and_board_survives_theme_switch(
    app,
    monkeypatch,
    theme,
    language,
    size,
):
    settings = AppSettings(theme=theme, language=language, fullscreen=False)
    monkeypatch.setattr(AppSettingsStore, "load", lambda self: settings)
    window = MainWindow()
    window.resize(*size)
    window.show()
    try:
        for screen in ScreenName:
            window.show_screen(screen)
            QTest.qWait(10)
            scroll = window._stack.currentWidget()
            assert isinstance(scroll, QScrollArea)
            assert scroll.horizontalScrollBar().maximum() == 0, screen
        game = window._game_screen
        assert game is not None
        game._start_new_game()
        game._on_board_square_clicked(chess.E2)
        board = game._board_widget
        before = board._board.fen()
        selection = board._selected_square
        window._apply_settings(settings)
        assert board._board.fen() == before
        assert board._selected_square == selection
        assert game._fen_label.isHidden() or not game._fen_label.isVisible()
        assert board._get_square_object_name(chess.E2) == "BoardSelectedSquare"
    finally:
        window.close()


def test_palette_roles_have_readable_text_contrast():
    def luminance(hex_color):
        rgb = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [
            c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb
        ]
        return sum(
            c * weight
            for c, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True)
        )

    for palette in (DARK, LIGHT):
        for foreground, background in (
            ("text_primary", "surface"),
            ("text_secondary", "surface_alt"),
            ("on_accent", "accent"),
        ):
            levels = sorted(
                (luminance(palette[foreground]), luminance(palette[background]))
            )
            assert (levels[1] + 0.05) / (levels[0] + 0.05) >= 4.5
        css = build_stylesheet(palette)
        for role in (
            "PrimaryButton",
            "SecondaryButton",
            "DangerButton",
            "Card",
            "SectionCard",
            "PageTitle",
            "SectionTitle",
            "HelperText",
            "StatusBadge",
            "StatCard",
        ):
            assert "#" + role in css


def test_backend_status_is_localized_without_modifying_result():
    set_language("pl")
    assert game_status("White to move. Check.") == "Na ruchu białe. Szach."
    set_language("en")
    assert game_status("Gracz poddał partię.") == "Player resigned."
    assert game_status("Game over. Result: 1/2-1/2.") == "Game over. Result: 1/2-1/2."
    set_language("pl")
