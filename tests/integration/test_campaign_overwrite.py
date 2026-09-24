import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog

from adaptive_chess.experiments.research import ResearchCampaign
from adaptive_chess.ui.campaign_files import create_campaign_file
from adaptive_chess.ui.screens.campaign_screen import CampaignScreen


def test_overwrite_retains_backup_and_rejects_old_window_save(tmp_path):
    path = tmp_path / "study.sqlite3"
    old = ResearchCampaign.create(path, "old", nodes=10)
    old.resume().play_human_move_uci("e2e4")
    old_document = ResearchCampaign(path).data
    created, backup = create_campaign_file(path, overwrite=True, participant="new")
    assert created.data["participant"] == "new"
    assert created.data["id"] != old_document["id"]
    assert created.data["active"] is None
    assert created.revision > old.revision
    assert backup is not None
    assert ResearchCampaign(backup).data == old_document
    with pytest.raises(RuntimeError, match="innym oknie"):
        old.save()
    assert ResearchCampaign(path).data == created.data


@pytest.mark.parametrize(
    "settings", [{"participant": ""}, {"participant": "new", "nodes": 0}]
)
def test_invalid_replacement_leaves_original_unchanged(tmp_path, settings):
    path = tmp_path / "study.sqlite3"
    ResearchCampaign.create(path, "old")
    before = path.read_bytes()
    with pytest.raises(ValueError):
        create_campaign_file(path, overwrite=True, **settings)
    assert path.read_bytes() == before
    assert not (tmp_path / "backups").exists()


def test_backup_failure_does_not_replace_original(tmp_path):
    path = tmp_path / "study.sqlite3"
    original = ResearchCampaign.create(path, "old").data
    (tmp_path / "backups").write_text("not a directory")
    with pytest.raises(OSError):
        create_campaign_file(path, overwrite=True, participant="new")
    assert ResearchCampaign(path).data == original


def test_backend_create_remains_exclusive(tmp_path):
    path = tmp_path / "study.sqlite3"
    original, backup = create_campaign_file(path, participant="old")
    assert backup is None
    with pytest.raises(FileExistsError):
        create_campaign_file(path, participant="new")
    assert ResearchCampaign(path).data == original.data


@pytest.mark.parametrize("accepted", [False, True])
def test_save_dialog_confirmation_is_honored(tmp_path, monkeypatch, accepted):
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "study.sqlite3"
    original = ResearchCampaign.create(path, "old").data
    screen = CampaignScreen(lambda: None)
    screen._participant.setText("new")
    monkeypatch.setattr(screen, "_resume", lambda: None)

    def dialog_exec(dialog):
        assert dialog.defaultSuffix() == "sqlite3"
        assert dialog.acceptMode() == QFileDialog.AcceptMode.AcceptSave
        assert not dialog.testOption(QFileDialog.Option.DontConfirmOverwrite)
        return QDialog.DialogCode.Accepted if accepted else QDialog.DialogCode.Rejected

    monkeypatch.setattr(QFileDialog, "exec", dialog_exec)
    monkeypatch.setattr(QFileDialog, "selectedFiles", lambda self: [str(path)])
    try:
        screen._create()
        app.processEvents()
        saved = ResearchCampaign(path)
        if accepted:
            assert saved.data["participant"] == "new"
            assert "backups" in screen._backup_notice.text()
            assert not screen._backup_notice.isHidden()
        else:
            assert saved.data == original
            assert not (tmp_path / "backups").exists()
    finally:
        screen.close()
