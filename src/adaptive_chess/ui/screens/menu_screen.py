from collections.abc import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
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
        on_campaign_clicked: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._on_play_clicked = on_play_clicked
        self._on_experiments_clicked = on_experiments_clicked
        self._on_results_clicked = on_results_clicked
        self._on_settings_clicked = on_settings_clicked
        self._on_exit_clicked = on_exit_clicked
        self._on_campaign_clicked = on_campaign_clicked

        self._build_ui()

    def _build_ui(self) -> None:
        from adaptive_chess.ui.widgets.components import (
            ActionCard,
            ResponsiveColumns,
            label,
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        content = QWidget()
        content.setMaximumWidth(1060)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(content, 10)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addSpacing(8)
        layout.addWidget(label("AdaptiveChessAI", "PageTitle"))
        layout.addWidget(label("Pracownia adaptacyjnych agentów szachowych"))
        layout.addSpacing(8)
        if self._on_campaign_clicked is not None:
            layout.addWidget(
                ActionCard(
                    "Kampania badawcza",
                    "Trenuj cztery metody na swoich partiach. "
                    "Wznawiaj zapis i oceniaj checkpointy.",
                    self._on_campaign_clicked,
                    featured=True,
                )
            )
        layout.addWidget(
            ResponsiveColumns(
                ActionCard(
                    "Gra swobodna",
                    "Zagraj z wybranym botem poza kampanią.",
                    self._on_play_clicked,
                ),
                ActionCard(
                    "Eksperymenty",
                    "Uruchom automatyczne porównania botów.",
                    self._on_experiments_clicked,
                ),
                ActionCard(
                    "Wyniki",
                    "Przejrzyj podsumowania, wykresy i tabele badań.",
                    self._on_results_clicked,
                ),
                breakpoint=600,
            )
        )
        footer = QHBoxLayout()
        for text, action in (
            ("Ustawienia", self._on_settings_clicked),
            ("Wyjście", self._on_exit_clicked),
        ):
            button = QPushButton(text)
            button.setObjectName("SecondaryButton")
            button.clicked.connect(action)
            footer.addWidget(button)
        footer.addStretch()
        layout.addLayout(footer)
