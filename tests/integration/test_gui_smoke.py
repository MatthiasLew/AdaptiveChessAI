import os
import time

# Qt nie potrzebuje prawdziwego monitora podczas testów.
# Musi być ustawione przed importem PySide6.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import chess
import pytest
from PySide6.QtWidgets import QApplication

from adaptive_chess.ui.app_settings import (
    AppSettings,
    AppSettingsStore,
)
from adaptive_chess.ui.main_window import MainWindow
from adaptive_chess.ui.navigation import ScreenName


@pytest.fixture(scope="session")
def qapp():
    """
    Zapewnia jedną instancję QApplication dla testów GUI.
    """
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


@pytest.fixture
def main_window(qapp, monkeypatch):
    """
    Tworzy MainWindow z kontrolowanymi ustawieniami.

    Nie korzystamy tutaj z prawdziwych ustawień użytkownika,
    ponieważ test powinien być deterministyczny.
    """

    test_settings = AppSettings(
        default_bot="random",
        default_human_color="white",
        default_depth=1,
        default_experiment_output_dir="results/gui_smoke_test",
    )

    monkeypatch.setattr(
        AppSettingsStore,
        "load",
        lambda self: test_settings,
    )

    window = MainWindow()

    yield window

    window.close()


def test_main_window_can_be_created(main_window):
    """
    Najważniejszy smoke test.

    Samo utworzenie MainWindow sprawdza, czy wszystkie ekrany
    posiadają API oczekiwane przez główne okno.
    """
    assert main_window is not None


def test_application_starts_on_menu(main_window):
    expected_index = main_window._screens[ScreenName.MENU]

    assert main_window._stack.currentIndex() == expected_index


@pytest.mark.parametrize(
    "screen_name",
    [
        ScreenName.MENU,
        ScreenName.GAME,
        ScreenName.GAME_SUMMARY,
        ScreenName.EXPERIMENTS,
        ScreenName.RESULTS,
        ScreenName.SETTINGS,
    ],
)
def test_all_registered_screens_can_be_opened(
        main_window,
        screen_name,
):
    """
    Sprawdza całą nawigację aplikacji.
    """
    main_window.show_screen(screen_name)

    expected_index = main_window._screens[screen_name]

    assert main_window._stack.currentIndex() == expected_index


def test_saved_settings_are_applied_to_game_screen(main_window):
    game_screen = main_window._game_screen

    assert game_screen is not None

    assert game_screen._bot_combo.currentData() == "random"
    assert game_screen._human_color_combo.currentData() == "white"
    assert game_screen._depth_spinbox.value() == 1


def test_saved_output_directory_is_applied_to_experiments_screen(
        main_window,
):
    experiments_screen = main_window._experiments_screen

    assert experiments_screen is not None

    assert experiments_screen._output_dir_edit.text() == "results/gui_smoke_test"


def test_new_game_flow_opens_game_screen(main_window):
    main_window.start_new_game_flow()

    expected_index = main_window._screens[ScreenName.GAME]

    assert main_window._stack.currentIndex() == expected_index


def test_random_game_can_be_started_from_gui(main_window):
    main_window.start_new_game_flow()

    game_screen = main_window._game_screen

    assert game_screen is not None

    game_screen._start_new_game()

    assert game_screen._session is not None
    assert game_screen._session.human_color == chess.WHITE
    assert game_screen._session.is_game_over() is False


def test_human_move_and_bot_response_work_through_game_screen(
        main_window,
):
    """
    Testuje połączenie:

    GameScreen
        -> HumanVsBotSession
        -> bot
        -> aktualizacja historii.
    """
    main_window.start_new_game_flow()

    game_screen = main_window._game_screen

    assert game_screen is not None

    game_screen._start_new_game()

    # Kliknięcie pionka e2.
    game_screen._on_board_square_clicked(chess.E2)

    # Kliknięcie pola e4.
    game_screen._on_board_square_clicked(chess.E4)
    deadline = time.monotonic() + 10
    while game_screen.thinking and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(0.005)
    assert not game_screen.thinking

    session = game_screen._session

    assert session is not None

    history = session.get_move_history()

    # ruch człowieka + odpowiedź RandomBota
    assert len(history) == 2

    assert history[0].player_type.value == "human"
    assert history[0].move_uci == "e2e4"

    assert history[1].player_type.value == "bot"


def test_unfinished_game_can_open_summary_screen(main_window):
    main_window.start_new_game_flow()

    game_screen = main_window._game_screen

    assert game_screen is not None

    game_screen._start_new_game()

    session = game_screen._session

    assert session is not None

    summary = session.get_current_game_summary()

    main_window.show_game_summary(summary)

    expected_index = main_window._screens[ScreenName.GAME_SUMMARY]

    assert main_window._stack.currentIndex() == expected_index


def test_play_again_returns_to_clean_game_screen(main_window):
    main_window.start_new_game_flow()

    game_screen = main_window._game_screen

    assert game_screen is not None

    game_screen._start_new_game()

    assert game_screen._session is not None

    # To jest to samo zachowanie, którego używa
    # przycisk "Graj ponownie" na ekranie podsumowania.
    main_window.start_new_game_flow()

    assert game_screen._session is None

    assert game_screen._history_list.count() == 0


def test_freeplay_runs_off_gui_thread_and_guards_close(main_window, monkeypatch):
    import threading

    from PySide6.QtGui import QCloseEvent
    main_window.start_new_game_flow()
    screen = main_window._game_screen
    screen._start_new_game()
    release = threading.Event()
    threads = []
    original = screen._session._bot.choose_move

    def slow_move(board):
        threads.append(threading.get_ident())
        assert release.wait(5)
        return original(board)

    monkeypatch.setattr(screen._session._bot, "choose_move", slow_move)
    try:
        screen._on_board_square_clicked(chess.E2)
        screen._on_board_square_clicked(chess.E4)
        assert screen.thinking
        event = QCloseEvent()
        main_window.closeEvent(event)
        assert not event.isAccepted()
    finally:
        release.set()
        deadline = time.monotonic() + 10
        while screen.thinking and time.monotonic() < deadline:
            QApplication.processEvents()
            time.sleep(0.005)
    assert not screen.thinking
    assert threads and threads[0] != threading.get_ident()
    assert len(screen._session.get_move_history()) == 2
