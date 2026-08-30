from enum import Enum


class ScreenName(str, Enum):
    """
    Nazwy ekranów aplikacji GUI.
    """

    MENU = "menu"
    GAME = "game"
    GAME_SUMMARY = "game_summary"
    EXPERIMENTS = "experiments"
    RESULTS = "results"
    SETTINGS = "settings"