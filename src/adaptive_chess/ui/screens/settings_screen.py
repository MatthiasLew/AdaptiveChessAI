from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SettingsScreen(QWidget):
    """
    Ekran ustawień aplikacji.
    """

    def __init__(
        self,
        on_back_to_menu_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        title = QLabel("Ustawienia")
        title.setObjectName("SectionTitle")

        panel = QFrame()
        panel.setObjectName("Panel")

        panel_layout = QVBoxLayout()
        panel_layout.setAlignment(Qt.AlignCenter)
        panel_layout.setSpacing(14)

        placeholder = QLabel("Tutaj pojawią się ustawienia aplikacji.")
        placeholder.setAlignment(Qt.AlignCenter)

        info = QLabel(
            "Docelowo: domyślny bot, kolor gracza, depth, folder wyników i motyw."
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)

        back_button = QPushButton("Powrót do menu")
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)

        panel_layout.addWidget(placeholder)
        panel_layout.addWidget(info)
        panel_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        panel.setLayout(panel_layout)

        root_layout.addWidget(title)
        root_layout.addWidget(panel, stretch=1)

        self.setLayout(root_layout)