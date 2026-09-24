"""Regression for a saved mating move hidden by campaign finalization failure."""

import os
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from adaptive_chess.experiments.research import ResearchCampaign
from adaptive_chess.ui.i18n import set_language
from adaptive_chess.ui.screens.campaign_screen import CampaignScreen

REPORTED_GAME = (
    "d4 d5 c3 Qd6 f3 Qg3+ hxg3 Nc6 e4 dxe4 fxe4 Nxd4 cxd4 Nf6 Qa4+ c6 "
    "Nc3 Nxe4 Nxe4 Be6 Nf3 Bxa2 Rxa2 O-O-O Qxa7 Rxd4 Nxd4 e6 Nd6+ Bxd6 "
    "Qa8+ Kd7 Qxh8 Bxg3+ Ke2 Kd6 Qxh7 f5 Qxg7 Kd5 Qxg3 Kxd4 Qg7+ e5 "
    "Qxb7 Kd5 Ke1 Kd4 Qxc6 f4 Qf6 Kd5 b3 Kd4 Bb2+ Kd5 Qxe5+ Kc6 Qxf4 "
    "Kd5 Ra1 Kc5 Rc1+ Kd5 Qe3 Kd6 Ke2 Kd5 g3 Kd6 Bh3 Kd5"
)


def saved_position(path, mate=False):
    campaign = ResearchCampaign.create(
        path, "regression", games=1, nodes=10, openings=[[]]
    )
    campaign.resume()
    board = chess.Board()
    for san in REPORTED_GAME.split():
        board.push_san(san)
    assert board.fen() == "8/8/8/3k4/8/1P2Q1PB/1B2K3/2R4R w - - 3 37"
    if mate:
        board.push_uci("h1d1")
        assert board.is_checkmate()
    campaign.data["active"]["moves"] = [m.uci() for m in board.move_stack]
    campaign.save()
    return board


def wait(screen, app):
    deadline = monotonic() + 45
    while screen.busy and monotonic() < deadline:
        app.processEvents()
        QTest.qWait(10)
    app.processEvents()
    assert not screen.busy


@pytest.fixture
def screen():
    app = QApplication.instance() or QApplication([])
    set_language("pl")
    widget = CampaignScreen(lambda: None)
    yield widget, app
    wait(widget, app)
    widget.close()


def test_reported_rook_mate_survives_disk_version_change(screen, tmp_path, monkeypatch):
    import adaptive_chess.experiments.research as module

    widget, app = screen
    path = tmp_path / "mate.sqlite3"
    saved_position(path)
    widget.load_campaign(path)
    widget._resume()
    wait(widget, app)
    monkeypatch.setattr(module, "environment_compatible", lambda saved: False)
    widget._click_square(chess.H1)
    assert chess.D1 in widget._board._legal_target_squares
    widget._click_square(chess.D1)
    wait(widget, app)
    assert "Wygrana" in widget._result_heading.text()
    assert widget._board._board.is_checkmate()
    assert not widget._reply_timer.isActive()
    saved = ResearchCampaign(path)
    assert saved.data["active"] is None
    assert saved.data["completed"][0]["result"] == "1-0"
    assert len(saved.data["completed"][0]["moves"]) == 73
    assert len(saved.data["models"]["td"]) == 2
    # A fresh session still requires a compatible environment.
    with pytest.raises(ValueError, match="środowisko"):
        saved.resume()


def test_finalization_error_shows_saved_mate_and_reload_recovers(
    screen, tmp_path, monkeypatch
):
    widget, app = screen
    path = tmp_path / "failure.sqlite3"
    saved_position(path)
    widget.load_campaign(path)
    widget._resume()
    wait(widget, app)

    def fail():
        raise ValueError("test finalization failure")

    monkeypatch.setattr(widget.campaign, "finish", fail)
    widget._click_square(chess.H1)
    widget._click_square(chess.D1)
    wait(widget, app)
    assert "test finalization failure" in widget._status.text()
    assert widget._pages.currentWidget() is widget._recovery
    assert str(path) in widget._current_file.text()
    assert not widget._resume_button.isVisible()
    assert widget._retry_load.isEnabled()
    assert widget._board._board.is_checkmate()
    assert not widget._board.isEnabled()
    saved = ResearchCampaign(path)
    assert len(saved.data["active"]["moves"]) == 73
    assert not saved.data["completed"]
    widget._retry_load.click()
    wait(widget, app)
    assert "Wygrana" in widget._result_heading.text()
    saved = ResearchCampaign(path)
    assert saved.data["active"] is None
    assert len(saved.data["completed"]) == 1
    widget.load_campaign(path)
    assert "Wygrana" in widget._result_heading.text()
    assert len(widget.campaign.data["completed"]) == 1


def test_version_error_has_actionable_recovery_and_retry(screen, tmp_path, monkeypatch):
    import adaptive_chess.experiments.research as module

    widget, app = screen
    path = tmp_path / "saved-mate.sqlite3"
    expected = saved_position(path, mate=True)
    original = module.environment_compatible
    monkeypatch.setattr(module, "environment_compatible", lambda saved: False)
    widget._load_and_resume(path)
    wait(widget, app)
    assert widget._pages.currentWidget() is widget._recovery
    assert "Samo ponawianie" in widget._recovery_message.text()
    assert "środowisko" in widget._recovery_details.text()
    assert not widget._recovery_disclosure.toggle.isChecked()
    assert widget._board._board.fen() == expected.fen()
    assert widget._campaign_path == path
    monkeypatch.setattr(module, "environment_compatible", original)
    widget._retry_load.click()
    wait(widget, app)
    assert widget._pages.currentWidget() is widget._play
    assert "Wygrana" in widget._result_heading.text()


def test_bad_file_can_be_replaced_directly_from_recovery(screen, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    widget, app = screen
    missing = tmp_path / "missing.sqlite3"
    good = tmp_path / "good.sqlite3"
    saved_position(good, mate=True)
    widget.load_campaign(missing)
    assert widget._pages.currentWidget() is widget._recovery
    assert str(missing) in widget._current_file.text()
    seen = []

    def select(*args):
        seen.append(args[2])
        return str(good), ""

    monkeypatch.setattr(QFileDialog, "getOpenFileName", select)
    widget._open()
    wait(widget, app)
    assert seen == [str(tmp_path)]
    assert widget._campaign_path == good
    assert "Wygrana" in widget._result_heading.text()
