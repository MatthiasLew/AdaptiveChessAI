from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
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
        self._fullscreen = QCheckBox("Uruchamiaj na pełnym ekranie")
        self._fullscreen.setToolTip("F11 przełącza pełny ekran, Esc wraca do okna.")
        self._delay = QSpinBox()
        self._delay.setRange(300, 3000)
        self._delay.setSingleStep(100)
        self._delay.setSuffix(" ms")
        self._bot_combo = QComboBox()
        self._color_combo = QComboBox()
        self._depth_combo = QComboBox()
        self._strength_help = QLabel()
        self._strength_help.setWordWrap(True)
        self._strength_help.setObjectName("HelperText")
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
        self._depth_combo.setCurrentIndex(settings.default_depth - 1)
        self._experiment_output_edit.setText(tr(settings.default_experiment_output_dir))

    def _build_ui(self) -> None:
        from adaptive_chess.ui.help_text import help_for
        from adaptive_chess.ui.widgets.components import (
            SectionCard,
            form_layout,
            label,
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)
        root.addWidget(label("Ustawienia", "PageTitle"))
        self._configure_controls()
        sections = (
            (
                "Wygląd",
                (
                    ("Język interfejsu", self._language_combo),
                    ("Wygląd", self._theme_combo),
                ),
            ),
            (
                "Gra",
                (
                    ("Domyślny bot", self._bot_combo),
                    ("Domyślny kolor gracza", self._color_combo),
                    ("Przewidywanie przeciwnika", self._depth_combo),
                    ("Pauza przed ruchem bota", self._delay),
                ),
            ),
            (
                "Badania / pliki",
                (("Domyślny folder eksperymentów", self._experiment_output_edit),),
            ),
        )
        for title, fields in sections:
            card = SectionCard(title)
            form = form_layout()
            for caption, widget in fields:
                field_label = label(caption)
                field_label.setBuddy(widget)
                form.addRow(field_label, widget)
            card.body.addLayout(form)
            if title == "Gra":
                card.body.addWidget(self._strength_help)
            if title == "Wygląd":
                card.body.addWidget(self._fullscreen)
            root.addWidget(card)
        help_for(self._depth_combo, "depth")
        help_for(self._experiment_output_edit, "files")
        actions = QHBoxLayout()
        for caption, action, role in (
            ("Zapisz ustawienia", self._save_settings, "PrimaryButton"),
            ("Przywróć domyślne", self._restore_defaults, "SecondaryButton"),
            ("Powrót do menu", self._on_back_to_menu_clicked, "SecondaryButton"),
        ):
            button = QPushButton(caption)
            button.setObjectName(role)
            button.clicked.connect(action)
            actions.addWidget(button)
        actions.addStretch()
        root.addLayout(actions)
        self._status_label.setObjectName("SaveStatusLabel")
        self._status_label.setWordWrap(True)
        root.addWidget(self._status_label)
        root.addStretch()

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

        for depth, caption in enumerate(
            ("1 — Szybkie", "2 — Umiarkowane", "3 — Dokładne", "4 — Najgłębsze"),
            start=1,
        ):
            self._depth_combo.addItem(tr(caption), depth)
        self._bot_combo.currentIndexChanged.connect(self.refresh_translation)
        self.refresh_translation()

    def refresh_translation(self) -> None:
        random = self._bot_combo.currentData() == BotKind.RANDOM.value
        self._depth_combo.setEnabled(not random)
        self._strength_help.setText(
            tr(
                "RandomBot wybiera losowe legalne ruchy. "
                "Poziom przewidywania nie wpływa na jego grę."
                if random
                else "Zakres 1-4: tyle półruchów bot analizuje w przód. "
                "1 jest najszybsze, 4 analizuje najgłębiej i może długo liczyć. "
                "Większa głębokość zwykle pomaga, ale nie gwarantuje wygranej. "
                "To nie jest ranking Elo."
            )
        )

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
            default_depth=int(self._depth_combo.currentData()),
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
        self._depth_combo.setCurrentIndex(defaults.default_depth - 1)
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
