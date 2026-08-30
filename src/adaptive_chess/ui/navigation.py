from enum import Enum


class ScreenName(str, Enum):
    """
    Nazwy ekranów aplikacji GUI.
    """

    MENU = "menu"
    GAME = "game"
    EXPERIMENTS = "experiments"
    RESULTS = "results"
    SETTINGS = "settings"