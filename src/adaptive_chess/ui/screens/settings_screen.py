from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.ui.app_settings import (
    AppSettings,
    AppSettingsStore,
)
from adaptive_chess.ui.bot_factory import BotKind
from adaptive_chess.ui.i18n import tr


class SettingsScreen(QWidget):
    """
    Ekran trwałych ustawień aplikacji.
    """

    def __init__(
        self,
        settings_store: AppSettingsStore,
        on_back_to_menu_clicked: Callable[[], None],
        on_settings_saved: Callable[[AppSettings], None],
    ) -> None:
        super().__init__()

        self._settings_store = settings_store
        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._on_settings_saved = on_settings_saved

        self._language_combo = QComboBox()
        self._language_combo.addItem("Polski", "pl")
        self._language_combo.addItem("English", "en")
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Ciemny", "dark")
        self._theme_combo.addItem("Jasny", "light")
        self._fullscreen = QCheckBox(
            "Uruchamiaj na pełnym ekranie (F11 przełącza, Esc wraca do okna)"
        )
        self._delay = QSpinBox()
        self._delay.setRange(300, 3000)
        self._delay.setSingleStep(100)
        self._delay.setSuffix(" ms")
        self._bot_combo = QComboBox()
        self._color_combo = QComboBox()
        self._depth_spinbox = QSpinBox()
        self._experiment_output_edit = QLineEdit()
        self._status_label = QLabel("")

        self._build_ui()
        self.reload_settings()

    def reload_settings(self) -> None:
        settings = self._settings_store.load()

        self._set_combo_by_data(
            self._bot_combo,
            settings.default_bot,
        )
        self._set_combo_by_data(
            self._color_combo,
            settings.default_human_color,
        )

        self._set_combo_by_data(self._language_combo, settings.language)
        self._set_combo_by_data(self._theme_combo, settings.theme)
        self._fullscreen.setChecked(settings.fullscreen)
        self._delay.setValue(settings.bot_delay_ms)
        self._depth_spinbox.setValue(settings.default_depth)
        self._experiment_output_edit.setText(tr(settings.default_experiment_output_dir))

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        title = QLabel("Ustawienia")
        title.setObjectName("SectionTitle")

        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QGridLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        self._configure_controls()

        save_button = QPushButton("Zapisz ustawienia")
        save_button.clicked.connect(self._save_settings)

        reset_button = QPushButton("Przywróć domyślne")
        reset_button.setObjectName("SecondaryButton")
        reset_button.clicked.connect(self._restore_defaults)

        back_button = QPushButton("Powrót do menu")
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)

        self._status_label.setObjectName("SaveStatusLabel")
        self._status_label.setWordWrap(True)

        layout.addWidget(QLabel("Domyślny bot"), 0, 0)
        layout.addWidget(self._bot_combo, 0, 1)

        layout.addWidget(QLabel("Domyślny kolor gracza"), 1, 0)
        layout.addWidget(self._color_combo, 1, 1)

        layout.addWidget(QLabel("Siła przewidywania ruchów"), 2, 0)
        layout.addWidget(self._depth_spinbox, 2, 1)

        layout.addWidget(QLabel("Domyślny folder eksperymentów"), 3, 0)
        layout.addWidget(self._experiment_output_edit, 3, 1)

        layout.addWidget(QLabel("Język interfejsu"), 4, 0)
        layout.addWidget(self._language_combo, 4, 1)
        layout.addWidget(QLabel("Wygląd"), 5, 0)
        layout.addWidget(self._theme_combo, 5, 1)
        layout.addWidget(self._fullscreen, 6, 0, 1, 2)
        layout.addWidget(QLabel("Pauza przed ruchem bota"), 7, 0)
        layout.addWidget(self._delay, 7, 1)
        layout.addWidget(save_button, 8, 0, 1, 2)
        layout.addWidget(reset_button, 9, 0, 1, 2)
        layout.addWidget(back_button, 10, 0, 1, 2)
        layout.addWidget(self._status_label, 11, 0, 1, 2)

        panel.setLayout(layout)

        root_layout.addWidget(title)
        root_layout.addWidget(panel)
        root_layout.addStretch()

        self.setLayout(root_layout)

    def _configure_controls(self) -> None:
        self._bot_combo.addItem(
            "RandomBot",
            BotKind.RANDOM.value,
        )
        self._bot_combo.addItem(
            "StaticMinimaxBot",
            BotKind.STATIC_MINIMAX.value,
        )
        self._bot_combo.addItem(
            "AdaptiveMinimaxBot",
            BotKind.ADAPTIVE_MINIMAX.value,
        )

        self._color_combo.addItem("Białe", "white")
        self._color_combo.addItem("Czarne", "black")

        self._depth_spinbox.setMinimum(1)
        self._depth_spinbox.setMaximum(4)

    def _save_settings(self) -> None:
        output_dir = self._experiment_output_edit.text().strip()

        if not output_dir:
            self._status_label.setText(tr("Folder eksperymentów nie może być pusty."))
            return

        settings = AppSettings(
            language=self._language_combo.currentData(),
            theme=self._theme_combo.currentData(),
            fullscreen=self._fullscreen.isChecked(),
            bot_delay_ms=self._delay.value(),
            default_bot=self._bot_combo.currentData(),
            default_human_color=self._color_combo.currentData(),
            default_depth=self._depth_spinbox.value(),
            default_experiment_output_dir=output_dir,
        )

        self._settings_store.save(settings)
        self._on_settings_saved(settings)

        self._status_label.setText(tr("Ustawienia zapisane."))

    def _restore_defaults(self) -> None:
        defaults = AppSettings()

        self._set_combo_by_data(
            self._bot_combo,
            defaults.default_bot,
        )
        self._set_combo_by_data(
            self._color_combo,
            defaults.default_human_color,
        )
        self._set_combo_by_data(self._language_combo, defaults.language)
        self._set_combo_by_data(self._theme_combo, defaults.theme)
        self._fullscreen.setChecked(defaults.fullscreen)
        self._delay.setValue(defaults.bot_delay_ms)
        self._depth_spinbox.setValue(defaults.default_depth)
        self._experiment_output_edit.setText(tr(defaults.default_experiment_output_dir))

        self._status_label.setText(
            tr("Przywrócono wartości domyślne. Kliknij „Zapisz ustawienia”.")
        )

    @staticmethod
    def _set_combo_by_data(
        combo: QComboBox,
        value: str,
    ) -> None:
        index = combo.findData(value)

        if index >= 0:
            combo.setCurrentIndex(index)
