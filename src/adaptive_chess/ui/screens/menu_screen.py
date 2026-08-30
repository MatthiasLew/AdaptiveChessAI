from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MenuScreen(QWidget):
    """
    Ekran startowy aplikacji.
    """

    def __init__(
        self,
        on_play_clicked: Callable[[], None],
        on_experiments_clicked: Callable[[], None],
        on_results_clicked: Callable[[], None],
        on_settings_clicked: Callable[[], None],
        on_exit_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_play_clicked = on_play_clicked
        self._on_experiments_clicked = on_experiments_clicked
        self._on_results_clicked = on_results_clicked
        self._on_settings_clicked = on_settings_clicked
        self._on_exit_clicked = on_exit_clicked

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        title = QLabel("AdaptiveChessAI")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Inteligentne szachy. Adaptacyjna nauka. Eksperymenty.")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        play_button = QPushButton("Graj z botem")
        experiments_button = QPushButton("Eksperymenty")
        results_button = QPushButton("Wyniki")
        settings_button = QPushButton("Ustawienia")
        exit_button = QPushButton("Wyjście")
        exit_button.setObjectName("DangerButton")

        for button in (
            play_button,
            experiments_button,
            results_button,
            settings_button,
            exit_button,
        ):
            button.setFixedWidth(280)

        play_button.clicked.connect(self._on_play_clicked)
        experiments_button.clicked.connect(self._on_experiments_clicked)
        results_button.clicked.connect(self._on_results_clicked)
        settings_button.clicked.connect(self._on_settings_clicked)
        exit_button.clicked.connect(self._on_exit_clicked)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(22)
        alignment = Qt.AlignmentFlag.AlignCenter
        layout.addWidget(play_button, alignment=alignment)
        layout.addWidget(experiments_button, alignment=alignment)
        layout.addWidget(results_button, alignment=alignment)
        layout.addWidget(settings_button, alignment=alignment)
        layout.addWidget(exit_button, alignment=alignment)

        self.setLayout(layout)
