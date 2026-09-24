import json
import os
from copy import deepcopy
from threading import Event
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from adaptive_chess.analysis.game_review import review_game
from adaptive_chess.experiments.arena import spectator_match
from adaptive_chess.experiments.research import ResearchCampaign
from adaptive_chess.ui.main_window import MainWindow
from adaptive_chess.ui.navigation import ScreenName
from adaptive_chess.ui.screens.campaign_screen import CampaignScreen


def wait_arena(dashboard, app):
    deadline = monotonic() + 20
    while dashboard.busy and monotonic() < deadline:
        app.processEvents()
        QTest.qWait(5)
    assert not dashboard.busy


def test_review_reports_a_provable_missed_mate_and_correct_material():
    # Black has Qh4# in the Fool's Mate position but chooses a6.
    moves = ["f2f3", "e7e5", "g2g4", "a7a6"]
    review = review_game(moves)
    assert review["missed_mates"] == [
        {"ply": 4, "side": "black", "played": "a6", "mate": "Qh4#"}
    ]
    assert not review_game([*moves[:3], "d8h4"])["missed_mates"]
    assert review["events"][-1]["material"] == 0


def test_spectator_cancellation_and_limit_do_not_mutate_research(tmp_path):
    campaign = ResearchCampaign.create(tmp_path / "arena.sqlite3", "test", nodes=10)
    before = deepcopy(campaign.data)
    white = campaign.data["models"]["td"][0]
    black = campaign.data["models"]["adaptive"][0]
    events = []
    cancel = Event()
    cancel.set()
    result = spectator_match(campaign, white, black, 20, 0, cancel, events.append)
    assert result["termination"] == "cancelled"
    assert result["moves"] == []
    cancel.clear()
    result = spectator_match(campaign, white, black, 2, 0, cancel, events.append)
    assert result["result"] == "*"
    assert result["termination"] == "move_limit"
    board = chess.Board()
    for uci in result["moves"]:
        board.push_uci(uci)
    assert board.fen() == result["final_fen"]
    assert campaign.data == before
    assert ResearchCampaign(campaign.path).data == before


def test_completed_campaign_shows_summary_and_runs_saved_bracket(tmp_path):
    app = QApplication.instance() or QApplication([])
    campaign = ResearchCampaign.create(
        tmp_path / "demo.sqlite3", "test", games=1, nodes=10
    )
    for _ in range(4):
        campaign.resume()
        campaign.finish(resign=True)
    original = campaign.path.read_bytes()
    screen = CampaignScreen(lambda: None)
    try:
        screen.load_campaign(campaign.path)
        dashboard = screen._dashboard
        assert screen._pages.currentWidget() is dashboard
        assert "Trening zakończony" in dashboard.summary.toPlainText()
        assert "Jeszcze nie wykonano benchmarku" in dashboard.benchmark.toPlainText()
        assert not screen._resume_button.isVisible()
        dashboard.limit.setValue(20)
        dashboard.pace.addItem("Test", 0)
        dashboard.pace.setCurrentIndex(dashboard.pace.count() - 1)
        for round_index in range(3):
            dashboard.start_match()
            assert screen.busy
            wait_arena(dashboard, app)
            assert len(dashboard.winners) == round_index + 1
        assert not dashboard.play.isEnabled()
        assert "Zwycięzca drabinki" in dashboard.bracket.text()
        saved = json.loads(dashboard.path.read_text(encoding="utf-8"))
        assert len(saved["results"]) == 3
        assert saved["results"][2]["slots"] == saved["winners"][:2]
        for result in saved["results"]:
            assert review_game(result["moves"])["final_fen"] == result["final_fen"]
        assert campaign.path.read_bytes() == original
        assert all(not selector.isEnabled() for selector in dashboard.slots)
        saved_path = dashboard.path
        dashboard.randomize()
        assert all(selector.isEnabled() for selector in dashboard.slots)
        assert not dashboard.winners
        dashboard.restore(saved_path)
        assert len(dashboard.winners) == 3
        assert len(dashboard.live.games) == 3
        assert not dashboard.play.isEnabled()
    finally:
        screen._dashboard.cancel()
        wait_arena(screen._dashboard, app)
        screen.close()


def test_escape_stops_visible_arena_without_advancing(tmp_path):
    app = QApplication.instance() or QApplication([])
    campaign = ResearchCampaign.create(tmp_path / "stop.sqlite3", "test", nodes=10)
    window = MainWindow()
    screen = window._campaign_screen
    try:
        screen.load_campaign(campaign.path)
        screen._show_dashboard()
        dashboard = screen._dashboard
        dashboard.tabs.setCurrentIndex(1)
        window.show_screen(ScreenName.CAMPAIGN)
        window.show()
        window.activateWindow()
        QTest.qWait(30)
        dashboard.start_match()
        QTest.keyClick(dashboard, Qt.Key.Key_Escape)
        wait_arena(dashboard, app)
        assert not dashboard.winners
        assert dashboard.records[-1]["termination"] == "cancelled"
        assert dashboard.play.isEnabled()
        assert not screen.thinking
    finally:
        screen._dashboard.cancel()
        wait_arena(screen._dashboard, app)
        window.close()
