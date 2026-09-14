import os
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

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
