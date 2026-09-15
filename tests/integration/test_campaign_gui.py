import os
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

from adaptive_chess.experiments.campaign import Campaign
from adaptive_chess.ui.screens.campaign_screen import CampaignScreen


def wait_worker(screen, app):
    deadline = monotonic() + 15
    while screen.busy and monotonic() < deadline:
        app.processEvents()
        QTest.qWait(5)
    assert not screen.busy
    assert not screen._error


def test_campaign_gui_move_worker_restart_and_frozen_tournament(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "campaign.sqlite3"
    Campaign.create(path, "gui-test", games=1)
    screen = CampaignScreen(lambda: None)
    try:
        screen.load_campaign(path)
        screen._resume()
        wait_worker(screen, app)
        screen._click_square(chess.E2)
        screen._click_square(chess.E4)
        wait_worker(screen, app)
        assert len(screen.campaign.session.get_move_history()) == 2
        expected = screen.campaign.session.get_fen()
        screen.load_campaign(path)
        screen._resume()
        wait_worker(screen, app)
        assert screen.campaign.session.get_fen() == expected
        assert screen.campaign.bot.opponent_profile.observed_moves == 1
        screen.campaign.finish(resign=True)
        screen._resume()
        wait_worker(screen, app)
        screen.campaign.finish(resign=True)
        screen._limit.setValue(20)
        screen._tournament()
        wait_worker(screen, app)
        assert len(screen.campaign.data["tournament"]["results"]) == 18
        assert screen.campaign.data["checkpoints"][-1]["profile"]["observed_moves"] == 1
    finally:
        screen.stop_tournament()
        if screen._worker:
            screen._worker.wait(15000)
        screen.close()


def test_four_method_gui_evaluation_process(tmp_path):
    from adaptive_chess.experiments.research import ResearchCampaign

    app = QApplication.instance() or QApplication([])
    path = tmp_path / "research.sqlite3"
    campaign = ResearchCampaign.create(path, "gui", games=1, nodes=10, openings=[[]])
    for _ in range(4):
        campaign.resume().play_human_move_uci("e2e4")
        campaign.finish(resign=True)
    screen = CampaignScreen(lambda: None)
    try:
        screen.load_campaign(path)
        screen._limit.setValue(20)
        screen._tournament()
        wait_worker(screen, app)
        assert len(screen.campaign.data["evaluations"]["results"]) == 16
        assert len(screen.campaign.data["tournament"]["results"]) == 12
        assert (tmp_path / "research_report" / "games.pgn").is_file()
    finally:
        screen.stop_tournament()
        screen.close()


def test_entry_separates_campaign_selection_from_play():
    app = QApplication.instance() or QApplication([])
    screen = CampaignScreen(lambda: None)
    screen.show()
    try:
        assert screen._pages.currentWidget() is screen._entry
        assert not screen._board.isVisible()
        new = next(
            b for b in screen.findChildren(QPushButton) if b.text() == "Nowa kampania"
        )
        new.click()
        app.processEvents()
        assert screen._pages.currentWidget() is screen._setup
        assert not screen._board.isVisible()
    finally:
        screen.close()


def test_human_move_is_visible_before_delayed_bot_reply(tmp_path):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "delay.sqlite3"
    Campaign.create(path, "gui", games=1)
    screen = CampaignScreen(lambda: None)
    try:
        screen.load_campaign(path)
        screen._resume()
        wait_worker(screen, app)
        screen._click_square(chess.E2)
        screen._click_square(chess.E4)
        deadline = monotonic() + 5
        while screen._worker and monotonic() < deadline:
            app.processEvents()
            QTest.qWait(5)
        assert screen._reply_timer.isActive()
        assert len(screen.campaign.session.get_move_history()) == 1
        assert screen._board._board.piece_at(chess.E4).piece_type == chess.PAWN
        assert not screen._board.isEnabled()
        assert screen.thinking
        wait_worker(screen, app)
        last = screen.campaign.session.get_move_history()[-1]
        assert last.player_type.value == "bot"
        assert "Bot:" in screen._status.text()
        assert last.move_uci[:2] in screen._status.text()
        assert (
            screen._board._get_square_object_name(
                chess.parse_square(last.move_uci[2:4])
            )
            == "BoardLastMoveSquare"
        )
    finally:
        wait_worker(screen, app)
        screen.close()


@pytest.mark.parametrize("move,expected", [("g6g7", "Wygrana"), ("g6f5", "Remis")])
def test_game_end_keeps_result_and_board_until_next_click(tmp_path, move, expected):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "ending.sqlite3"
    campaign = Campaign.create(path, "gui", games=2)
    campaign.data["initial_fen"] = "7k/5K2/6Q1/8/8/8/8/8 w - - 0 1"
    campaign.save()
    screen = CampaignScreen(lambda: None)
    try:
        screen.load_campaign(path)
        screen._resume()
        wait_worker(screen, app)
        screen._click_square(chess.parse_square(move[:2]))
        screen._click_square(chess.parse_square(move[2:]))
        wait_worker(screen, app)
        assert expected in screen._result_heading.text()
        assert screen.campaign.session is None
        assert screen.campaign.data["active"] is None
        record = screen.campaign.data["completed"][-1]
        assert screen._board._board.fen() == record["final_fen"]
        QTest.qWait(1000)
        assert len(screen.campaign.data["completed"]) == 1
        assert screen.campaign.data["active"] is None
        screen.load_campaign(path)
        assert expected in screen._result_heading.text()
        screen._resume_button.click()
        wait_worker(screen, app)
        assert screen.campaign.data["active"] is not None
        assert not screen._result_heading.text()
    finally:
        wait_worker(screen, app)
        screen.close()
