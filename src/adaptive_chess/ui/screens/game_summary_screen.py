from collections.abc import Callable
from pathlib import Path

import chess
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.play.game_exporter import write_game_summary_exports
from adaptive_chess.play.human_vs_bot_session import HumanVsBotGameSummary
from adaptive_chess.ui.help_text import help_for
from adaptive_chess.ui.i18n import game_status, tr
from adaptive_chess.ui.summary_formatter import (
    color_to_polish,
    describe_result,
)
from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget
from adaptive_chess.ui.widgets.components import (
    BoardArea,
    Disclosure,
    ResponsiveColumns,
    SectionCard,
    form_layout,
    label,
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
        self._board_widget = ChessBoardWidget()
        self._position_help = label("")

        self._build_ui()

    def set_summary(self, summary: HumanVsBotGameSummary) -> None:
        """
        Ustawia dane zakończonej partii.
        """
        self._summary = summary
        self._save_status_label.clear()
        self._save_status_label.hide()

        self._result_label.setText(
            f"{summary.result} — {tr(describe_result(summary.result))}"
        )
        self._status_label.setText(game_status(summary.status_message))
        self._bot_label.setText(tr(summary.bot_name))
        self._human_color_label.setText(tr(color_to_polish(summary.human_color)))
        self._half_moves_label.setText(tr(str(summary.half_moves)))
        balance = summary.final_material_balance
        self._material_label.setText(
            tr("Białe +{value}" if balance > 0 else "Czarne +{value}").format(
                value=abs(balance)
            )
            if balance
            else tr("Równy materiał")
        )
        self._fen_label.setText(tr(summary.final_fen))
        board = chess.Board(summary.final_fen)
        self._board_widget.set_flipped(summary.human_color == chess.BLACK)
        self._board_widget.clear_highlights()
        self._board_widget.set_board(
            board,
            last_move=chess.Move.from_uci(summary.move_history[-1].move_uci)
            if summary.move_history
            else None,
        )
        if board.is_check():
            self._board_widget.set_selected_square(board.king(board.turn))
        if board.is_checkmate():
            self._position_help.setText(
                tr(
                    "Mat: zaznaczony król jest szachowany. Legalne odpowiedzi: 0. "
                    "Nie można uciec królem, zbić szachującej figury "
                    "ani zasłonić szacha."
                )
            )
        elif board.is_stalemate():
            self._position_help.setText(
                tr(
                    "Pat: król nie jest szachowany, ale strona na ruchu nie ma "
                    "legalnego ruchu. To remis."
                )
            )
        else:
            self._position_help.setText(
                tr(
                    "Końcowa pozycja do obejrzenia. "
                    "Powód zakończenia podano przy wyniku."
                )
            )

        self._history_list.clear()

        for index, move in enumerate(summary.move_history, start=1):
            color = "Białe" if move.color == chess.WHITE else "Czarne"
            player = "gracz" if move.player_type.value == "human" else "bot"

            self._history_list.addItem(
                f"{index:02d}. {tr(color)} {tr(player)}: {move.san}"
            )

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)
        root.addWidget(label("Podsumowanie partii", "PageTitle"))
        panel = SectionCard()
        panel.body.setContentsMargins(12, 12, 12, 12)
        panel.body.setSpacing(8)
        self._result_label.setObjectName("SummaryResultLabel")
        self._result_label.setWordWrap(True)
        self._status_label.setWordWrap(True)
        panel.body.addWidget(self._result_label)
        panel.body.addWidget(self._status_label)
        panel.body.addWidget(self._position_help)
        tabs = QTabWidget()
        tabs.addTab(self._history_list, tr("Historia ruchów"))
        details = QWidget()
        form = form_layout()
        details.setLayout(form)
        for caption, value in (
            ("Bot", self._bot_label),
            ("Kolor gracza", self._human_color_label),
            ("Liczba półruchów", self._half_moves_label),
            ("Końcowy materiał", self._material_label),
        ):
            form.addRow(label(caption), value)
        self._fen_label.setWordWrap(True)
        help_for(self._fen_label, "fen")
        form.addRow(Disclosure("Końcowy FEN", self._fen_label))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(details)
        tabs.addTab(scroll, tr("Szczegóły techniczne"))
        panel.body.addWidget(tabs, 1)
        panel.setMinimumWidth(300)
        root.addWidget(
            ResponsiveColumns(BoardArea(self._board_widget), panel, breakpoint=700), 1
        )
        buttons = QHBoxLayout()
        for caption, callback, role in (
            ("Zapisz partię", self._save_summary, "SecondaryButton"),
            ("Graj ponownie", self._on_play_again_clicked, "PrimaryButton"),
            ("Powrót do menu", self._on_back_to_menu_clicked, "BackButton"),
        ):
            button = QPushButton(caption)
            button.setObjectName(role)
            button.clicked.connect(callback)
            buttons.addWidget(button)
            if caption == "Zapisz partię":
                help_for(button, "files")
        root.addLayout(buttons)
        self._save_status_label.setWordWrap(True)
        self._save_status_label.hide()
        root.addWidget(self._save_status_label)

    def heightForWidth(self, width: int) -> int:
        return self.layout().minimumHeightForWidth(width)

    def _save_summary(self) -> None:
        self._save_status_label.show()
        if self._summary is None:
            self._save_status_label.setText(tr("Brak partii do zapisania."))
            return

        try:
            json_path, csv_path = write_game_summary_exports(
                summary=self._summary,
                output_dir=DEFAULT_HUMAN_GAME_RESULTS_DIR,
            )
        except OSError as error:
            self._save_status_label.setText(
                tr(f"Nie udało się zapisać partii: {error}")
            )
            return

        self._save_status_label.setText(
            tr(f"Zapisano partię:\nJSON: {json_path}\nCSV: {csv_path}")
        )
