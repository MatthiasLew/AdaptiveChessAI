from collections.abc import Callable
from pathlib import Path

import chess

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.play.game_exporter import write_game_summary_exports
from adaptive_chess.play.human_vs_bot_session import HumanVsBotGameSummary
from adaptive_chess.ui.summary_formatter import (
    color_to_polish,
    describe_material_balance,
    describe_result,
)


DEFAULT_HUMAN_GAME_RESULTS_DIR = Path("results") / "human_games"


class GameSummaryScreen(QWidget):
    """
    Ekran podsumowania zakończonej partii człowiek vs bot.
    """

    def __init__(
        self,
        on_play_again_clicked: Callable[[], None],
        on_back_to_menu_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_play_again_clicked = on_play_again_clicked
        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._summary: HumanVsBotGameSummary | None = None

        self._result_label = QLabel("Brak zakończonej partii.")
        self._status_label = QLabel("-")
        self._bot_label = QLabel("-")
        self._human_color_label = QLabel("-")
        self._half_moves_label = QLabel("-")
        self._material_label = QLabel("-")
        self._fen_label = QLabel("-")
        self._save_status_label = QLabel("")
        self._history_list = QListWidget()

        self._build_ui()

    def set_summary(self, summary: HumanVsBotGameSummary) -> None:
        """
        Ustawia dane zakończonej partii.
        """
        self._summary = summary
        self._save_status_label.setText("")

        self._result_label.setText(
            f"{summary.result} — {describe_result(summary.result)}"
        )
        self._status_label.setText(summary.status_message)
        self._bot_label.setText(summary.bot_name)
        self._human_color_label.setText(color_to_polish(summary.human_color))
        self._half_moves_label.setText(str(summary.half_moves))
        self._material_label.setText(
            describe_material_balance(summary.final_material_balance)
        )
        self._fen_label.setText(summary.final_fen)

        self._history_list.clear()

        for index, move in enumerate(summary.move_history, start=1):
            color = "Białe" if move.color == chess.WHITE else "Czarne"
            player = "gracz" if move.player_type.value == "human" else "bot"

            self._history_list.addItem(
                f"{index:02d}. {color} {player}: "
                f"{move.san} ({move.move_uci})"
            )

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        title = QLabel("Podsumowanie partii")
        title.setObjectName("SectionTitle")

        content_panel = QFrame()
        content_panel.setObjectName("Panel")

        content_layout = QGridLayout()
        content_layout.setContentsMargins(22, 22, 22, 22)
        content_layout.setSpacing(14)

        self._result_label.setObjectName("SummaryResultLabel")
        self._status_label.setWordWrap(True)
        self._fen_label.setWordWrap(True)
        self._fen_label.setObjectName("FenLabel")
        self._save_status_label.setObjectName("SaveStatusLabel")
        self._save_status_label.setWordWrap(True)

        content_layout.addWidget(QLabel("Wynik"), 0, 0)
        content_layout.addWidget(self._result_label, 0, 1)

        content_layout.addWidget(QLabel("Status"), 1, 0)
        content_layout.addWidget(self._status_label, 1, 1)

        content_layout.addWidget(QLabel("Bot"), 2, 0)
        content_layout.addWidget(self._bot_label, 2, 1)

        content_layout.addWidget(QLabel("Kolor gracza"), 3, 0)
        content_layout.addWidget(self._human_color_label, 3, 1)

        content_layout.addWidget(QLabel("Liczba półruchów"), 4, 0)
        content_layout.addWidget(self._half_moves_label, 4, 1)

        content_layout.addWidget(QLabel("Końcowy materiał"), 5, 0)
        content_layout.addWidget(self._material_label, 5, 1)

        content_layout.addWidget(QLabel("Końcowy FEN"), 6, 0)
        content_layout.addWidget(self._fen_label, 6, 1)

        history_title = QLabel("Historia ruchów")
        history_title.setObjectName("SectionTitle")

        content_layout.addWidget(history_title, 7, 0, 1, 2)
        content_layout.addWidget(self._history_list, 8, 0, 1, 2)

        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(10)

        save_button = QPushButton("Zapisz partię")
        save_button.clicked.connect(self._save_summary)

        play_again_button = QPushButton("Graj ponownie")
        play_again_button.clicked.connect(self._on_play_again_clicked)

        menu_button = QPushButton("Powrót do menu")
        menu_button.setObjectName("SecondaryButton")
        menu_button.clicked.connect(self._on_back_to_menu_clicked)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(play_again_button)
        buttons_layout.addWidget(menu_button)

        content_layout.addLayout(buttons_layout, 9, 0, 1, 2)
        content_layout.addWidget(self._save_status_label, 10, 0, 1, 2)

        content_panel.setLayout(content_layout)

        root_layout.addWidget(title)
        root_layout.addWidget(content_panel, stretch=1)

        self.setLayout(root_layout)

    def _save_summary(self) -> None:
        if self._summary is None:
            self._save_status_label.setText("Brak partii do zapisania.")
            return

        try:
            json_path, csv_path = write_game_summary_exports(
                summary=self._summary,
                output_dir=DEFAULT_HUMAN_GAME_RESULTS_DIR,
            )
        except OSError as error:
            self._save_status_label.setText(f"Nie udało się zapisać partii: {error}")
            return

        self._save_status_label.setText(
            "Zapisano partię:\n"
            f"JSON: {json_path}\n"
            f"CSV: {csv_path}"
        )