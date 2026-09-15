import os
from time import monotonic

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton

from adaptive_chess.ui.app_settings import AppSettings, AppSettingsStore
from adaptive_chess.ui.i18n import set_language
from adaptive_chess.ui.main_window import MainWindow
from adaptive_chess.ui.screens.experiments_screen import ExperimentsScreen
from adaptive_chess.ui.screens.results_screen import ResultsScreen
from adaptive_chess.ui.theme import LIGHT


@pytest.fixture
def app():
    application = QApplication.instance() or QApplication([])
    style = application.styleSheet()
    set_language("pl")
    yield application
    set_language("pl")
    application.setStyleSheet(style)


def test_preferences_persist_in_separate_settings_file(tmp_path):
    store = AppSettingsStore()
    store._settings = QSettings(
        str(tmp_path / "settings.ini"), QSettings.Format.IniFormat
    )
    expected = AppSettings(
        language="en", theme="light", fullscreen=False, bot_delay_ms=1500
    )
    store.save(expected)
    assert store.load() == expected


def test_fullscreen_start_and_keyboard_escape(app, monkeypatch):
    monkeypatch.setattr(AppSettingsStore, "load", lambda self: AppSettings())
    window = MainWindow()
    try:
        window.show_startup()
        app.processEvents()
        assert window.isFullScreen()
        window.leave_fullscreen()
        assert not window.isFullScreen()
        window.toggle_fullscreen()
        assert window.isFullScreen()
    finally:
        window.close()


def test_theme_language_and_delay_apply_without_losing_campaign(app, monkeypatch):
    monkeypatch.setattr(AppSettingsStore, "load", lambda self: AppSettings())
    window = MainWindow()
    try:
        screen = window._campaign_screen
        window._apply_settings(
            AppSettings(language="en", theme="light", bot_delay_ms=1700)
        )
        captions = {b.text() for b in window.findChildren(QPushButton)}
        assert "Save settings" in captions
        assert any(
            b.accessibleName() == "Research campaign"
            for b in window.findChildren(QPushButton)
        )
        assert LIGHT["background"] in app.styleSheet()
        assert screen._reply_timer.interval() == 1700
        window._apply_settings(AppSettings())
        assert any(
            b.accessibleName() == "Kampania badawcza"
            for b in window.findChildren(QPushButton)
        )
        assert window._campaign_screen is screen
    finally:
        window.close()


def test_reports_render_markdown_and_hide_technical_files(app, tmp_path):
    (tmp_path / "report.md").write_text(
        "# Czytelny raport\n\n**Wynik**", encoding="utf-8"
    )
    (tmp_path / "metadata.json").write_text('{"matches_count": 2}', encoding="utf-8")
    screen = ResultsScreen(lambda: None)
    try:
        screen._folder_edit.setText(str(tmp_path))
        screen._load_results_folder()
        assert screen._files_list.count() == 1
        screen._files_list.setCurrentRow(0)
        assert "# Czytelny" not in screen._preview.toPlainText()
        assert "Czytelny raport" in screen._preview.toPlainText()
        screen._technical.setChecked(True)
        assert screen._files_list.count() == 2
    finally:
        screen.close()


def test_full_suite_runs_from_gui_and_reports_readable_results(
    app, tmp_path, monkeypatch
):
    # Reproduce the user's missing-import failure without inherited PYTHONPATH.
    monkeypatch.delenv("PYTHONPATH", raising=False)
    screen = ExperimentsScreen(lambda: None)
    try:
        screen._matches_spinbox.setValue(1)
        screen._max_half_moves_spinbox.setValue(2)
        screen._output_dir_edit.setText(str(tmp_path))
        assert not screen._details.isChecked()
        screen._start_experiment()
        deadline = monotonic() + 120
        while screen._is_process_running() and monotonic() < deadline:
            app.processEvents()
            QTest.qWait(30)
        assert not screen._is_process_running()
        app.processEvents()
        assert screen._process.exitCode() == 0, screen._log_output.toPlainText()
        assert (tmp_path / "suite_summary.md").is_file()
        assert "Podsumowanie" in screen._report.toPlainText()
        assert "Przerwane limitem" in screen._report.toPlainText()
        assert "\ufffd" not in screen._log_output.toPlainText()
    finally:
        if screen._is_process_running():
            screen._process.kill()
            screen._process.waitForFinished(5000)
        screen.close()
