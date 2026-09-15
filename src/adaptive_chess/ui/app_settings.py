from dataclasses import dataclass

from PySide6.QtCore import QSettings

ORGANIZATION_NAME = "AdaptiveChessAI"
APPLICATION_NAME = "AdaptiveChessAI"


@dataclass(frozen=True)
class AppSettings:
    language: str = "pl"
    theme: str = "dark"
    fullscreen: bool = True
    bot_delay_ms: int = 850
    default_bot: str = "random"
    default_human_color: str = "white"
    default_depth: int = 1
    default_experiment_output_dir: str = "results/gui_experiments"


class AppSettingsStore:
    """
    Obsługuje trwałe ustawienia aplikacji przez QSettings.
    """

    def __init__(self) -> None:
        self._settings = QSettings(
            ORGANIZATION_NAME,
            APPLICATION_NAME,
        )

    def load(self) -> AppSettings:
        default_bot = self._settings.value(
            "game/default_bot",
            "random",
            type=str,
        )
        default_human_color = self._settings.value(
            "game/default_human_color",
            "white",
            type=str,
        )
        default_depth = self._settings.value(
            "game/default_depth",
            1,
            type=int,
        )
        default_output_dir = self._settings.value(
            "experiments/default_output_dir",
            "results/gui_experiments",
            type=str,
        )

        if not isinstance(default_bot, str):
            default_bot = "random"
        if not isinstance(default_human_color, str):
            default_human_color = "white"
        if not isinstance(default_depth, int):
            default_depth = 1
        if not isinstance(default_output_dir, str):
            default_output_dir = "results/gui_experiments"

        language = self._settings.value("ui/language", "pl", type=str)
        theme = self._settings.value("ui/theme", "dark", type=str)
        return AppSettings(
            language=language if language in ("pl", "en") else "pl",
            theme=theme if theme in ("dark", "light") else "dark",
            fullscreen=self._settings.value("ui/fullscreen", True, type=bool),
            bot_delay_ms=max(
                300, min(3000, self._settings.value("ui/bot_delay_ms", 850, type=int))
            ),
            default_bot=default_bot,
            default_human_color=default_human_color,
            default_depth=default_depth,
            default_experiment_output_dir=default_output_dir,
        )

    def save(self, settings: AppSettings) -> None:
        self._settings.setValue(
            "game/default_bot",
            settings.default_bot,
        )
        self._settings.setValue(
            "game/default_human_color",
            settings.default_human_color,
        )
        self._settings.setValue(
            "game/default_depth",
            settings.default_depth,
        )
        self._settings.setValue(
            "experiments/default_output_dir",
            settings.default_experiment_output_dir,
        )

        for key in ("language", "theme", "fullscreen", "bot_delay_ms"):
            self._settings.setValue(f"ui/{key}", getattr(settings, key))
        self._settings.sync()
