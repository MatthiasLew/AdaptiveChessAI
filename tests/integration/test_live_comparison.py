import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QStyle

from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.experiments.live_events import PREFIX
from adaptive_chess.experiments.match_runner import MatchRunner
from adaptive_chess.ui.i18n import set_language
from adaptive_chess.ui.screens.experiments_screen import ExperimentsScreen
from adaptive_chess.ui.theme import install_quick_tooltips


@pytest.fixture
def app():
    application = QApplication.instance() or QApplication([])
    set_language("pl")
    return application


def test_real_match_stream_replays_all_positions_and_keeps_rules(monkeypatch, capsys):
    monkeypatch.setenv("ADAPTIVE_CHESS_LIVE", "1")
    result = MatchRunner(max_half_moves=4).play(RandomBot(), RandomBot())
    events = [
        json.loads(line[len(PREFIX) :]) for line in capsys.readouterr().out.splitlines()
    ]
    assert [e["kind"] for e in events] == ["start", *["move"] * 4, "end"]
    board = chess.Board(events[0]["fen"])
    for event in events[1:-1]:
        move = chess.Move.from_uci(event["uci"])
        assert board.san(move) == event["san"]
        board.push(move)
        assert board.fen() == event["fen"]
    assert board.fen() == result.final_fen
    assert events[-1]["result"] == "*"
    assert result.reached_move_limit
    monkeypatch.delenv("ADAPTIVE_CHESS_LIVE")
    MatchRunner(max_half_moves=1).play(RandomBot(), RandomBot())
    assert not capsys.readouterr().out


def test_fragmented_stream_and_browsing_while_moves_arrive(app):
    screen = ExperimentsScreen(lambda: None)
    board = chess.Board()
    start = (
        PREFIX
        + json.dumps(
            {
                "kind": "start",
                "white": "StaticMinimaxBot",
                "black": "RandomBot",
                "fen": board.fen(),
            }
        )
        + "\n"
    )
    try:
        for character in start:
            screen._consume_output(character)
        view = screen._live_view
        QTest.qWait(100)
        assert len(view.games) == 1
        for ply, uci in enumerate(("e2e4", "e7e5"), 1):
            san = board.san(chess.Move.from_uci(uci))
            board.push_uci(uci)
            event = {
                "kind": "move",
                "ply": ply,
                "uci": uci,
                "san": san,
                "side": "white" if ply == 1 else "black",
                "fen": board.fen(),
                "material": 0,
            }
            screen._consume_output(PREFIX + json.dumps(event) + "\n")
            QTest.qWait(100)
            if ply == 1:
                view._step(-1)
        assert view.slider.value() == 0
        assert view.slider.maximum() == 2
        assert "1. e4" not in view.board.toPlainText()
        view.follow.setChecked(True)
        assert "1. e4 (e2e4)" in view.board.toPlainText()
        assert "1... e5 (e7e5)" in view.board.toPlainText()
        screen._consume_output("CHESS_EVENT {broken}\nordinary log", final=True)
        assert "ordinary log" in screen._log_output.toPlainText()
        assert "{broken}" in screen._log_output.toPlainText()
        view.reset()
        assert not view.games
        assert view.slider.maximum() == 0
    finally:
        screen.close()


def test_tooltips_have_short_wakeup_delay(app):
    install_quick_tooltips(app)
    assert app.style().styleHint(QStyle.StyleHint.SH_ToolTip_WakeUpDelay) == 150


def test_chart_preview_fits_viewport_after_resize(app, tmp_path):
    from PySide6.QtGui import QColor, QImage

    from adaptive_chess.ui.screens.results_screen import ResultsScreen

    picture = QImage(1500, 750, QImage.Format.Format_RGB32)
    picture.fill(QColor("white"))
    picture.save(str(tmp_path / "actual_results.png"))
    screen = ResultsScreen(lambda: None)
    screen._folder_edit.setText(str(tmp_path))
    screen._load_results_folder()
    screen._reports_disclosure.toggle.setChecked(True)
    screen.resize(1200, 1000)
    screen.show()
    try:
        screen._files_list.setCurrentRow(0)
        for width in (1200, 900):
            screen.resize(width, 1000)
            QTest.qWait(50)
            assert screen._preview.horizontalScrollBar().maximum() == 0
            assert screen._preview.verticalScrollBar().maximum() == 0
        from adaptive_chess.ui.widgets.chart_preview import ChartPreview

        assert screen._enlarge_chart.isVisible()
        screen._enlarge_chart.click()
        QTest.qWait(50)
        dialog = screen.findChild(ChartPreview)
        assert dialog.isVisible()
        dialog.set_fit(False)
        assert dialog.picture.pixmap().width() == 1500
        dialog.set_fit(True)
        assert dialog.picture.pixmap().width() <= dialog.scroll.viewport().width()
        dialog.close()
    finally:
        screen.close()
