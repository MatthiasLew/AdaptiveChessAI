from src.adaptive_chess.ui.navigation import ScreenName


def test_screen_names_are_stable():
    assert ScreenName.MENU.value == "menu"
    assert ScreenName.GAME.value == "game"
    assert ScreenName.EXPERIMENTS.value == "experiments"
    assert ScreenName.RESULTS.value == "results"
    assert ScreenName.SETTINGS.value == "settings"