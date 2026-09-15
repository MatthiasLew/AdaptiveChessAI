from collections.abc import Callable

import chess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.play.human_vs_bot_session import (
    HumanVsBotGameSummary,
    HumanVsBotSession,
)
from adaptive_chess.ui.bot_factory import (
    BotKind,
    create_bot_for_gui,
    parse_human_color,
)
from adaptive_chess.ui.help_text import help_for
from adaptive_chess.ui.i18n import game_status, tr
from adaptive_chess.ui.move_builder import (
    build_uci_move_from_clicks,
    get_legal_target_squares,
)
from adaptive_chess.ui.screens.campaign_screen import CampaignWorker
from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget
from adaptive_chess.ui.widgets.components import (
    BoardArea,
    Disclosure,
    SectionCard,
    form_layout,
    label,
)


class GameScreen(QWidget):
    """
    Ekran gry z botem.

    Obsługuje:
    - wybór bota,
    - wybór koloru,
    - wybór głębokości,
    - start nowej gry,
    - kliknięcia pól,
    - wykonanie ruchu człowieka,
    - odpowiedź bota,
    - historię ruchów,
    - status gry,
    - zakończenie i podsumowanie aktualnej partii.
    """

    def heightForWidth(self, width: int) -> int:
        # Wrapped labels must not force the preferred height of scrollable tabs.
        layout = self.layout()
        return layout.minimumHeightForWidth(width) if layout else -1

    def apply_defaults(
        self,
        bot_kind: str,
        human_color: str,
        depth: int,
    ) -> None:
        bot_index = self._bot_combo.findData(bot_kind)

        if bot_index >= 0:
            self._bot_combo.setCurrentIndex(bot_index)

        color_index = self._human_color_combo.findData(human_color)

        if color_index >= 0:
            self._human_color_combo.setCurrentIndex(color_index)

        self._depth_spinbox.setValue(depth)

    def __init__(
        self,
        on_back_to_menu_clicked: Callable[[], None],
        on_game_finished: Callable[[HumanVsBotGameSummary], None],
    ) -> None:
        super().__init__()

        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._on_game_finished = on_game_finished

        self._worker: CampaignWorker | None = None
        self._error = ""
        self._session: HumanVsBotSession | None = None
        self._selected_square: chess.Square | None = None

        self._board_widget = ChessBoardWidget()
        self._board_widget.square_clicked.connect(self._on_board_square_clicked)

        self._bot_combo = QComboBox()
        self._human_color_combo = QComboBox()
        self._depth_spinbox = QSpinBox()

        self._new_game_button = QPushButton("Nowa gra")
        self._finish_game_button = QPushButton("Zakończ i podsumuj")
        self._clear_game_button = QPushButton("Wyczyść partię")

        self._status_label = QLabel("Nie rozpoczęto gry.")
        self._fen_label = QLabel("-")
        self._history_list = QListWidget()

        self._build_ui()
        self.prepare_for_new_game()

    def prepare_for_new_game(self) -> None:
        """
        Przygotowuje ekran gry do rozpoczęcia nowej partii.

        Nie startuje automatycznie partii. Użytkownik nadal musi kliknąć
        przycisk „Nowa gra”, żeby utworzyć sesję.
        """
        if self.thinking:
            return
        self._session = None
        self._clear_selection()

        board = chess.Board()
        self._board_widget.set_flipped(False)
        self._board_widget.set_board(board)

        self._status_label.setText(tr("Wybierz ustawienia i kliknij „Nowa gra”."))
        self._fen_label.setText(tr(board.fen()))
        self._history_list.clear()
        self._agent_label.clear()
        self._agent_label.hide()
        self._game_tabs.setCurrentIndex(0)

        self._set_configuration_enabled(True)
        self._finish_game_button.setEnabled(False)
        self._clear_game_button.setEnabled(False)

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(16)

        title = QLabel("Gra z botem")
        title.setObjectName("PageTitle")

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        board_panel = self._build_board_panel()
        side_panel = self._build_side_panel()

        content_layout.addWidget(board_panel, stretch=3)
        content_layout.addWidget(side_panel, stretch=1)

        root_layout.addWidget(title)
        root_layout.addLayout(content_layout, stretch=1)

        self.setLayout(root_layout)

    def _build_board_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(BoardArea(self._board_widget), stretch=1)

        hint = QLabel(
            "Kliknij własną figurę, a potem pole docelowe. "
            "Po ruchu człowieka bot odpowie automatycznie."
        )
        hint.setObjectName("SubtitleLabel")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._board_widget.setToolTip(hint.text())
        hint.deleteLater()
        panel.setLayout(layout)

        return panel

    def _build_side_panel(self) -> QFrame:
        panel = SectionCard()
        panel.setMinimumWidth(300)
        panel.body.setSpacing(8)
        panel.body.setContentsMargins(12, 12, 12, 12)
        layout = panel.body
        self._configure_bot_combo()
        self._configure_human_color_combo()
        self._configure_depth_spinbox()
        self._configure_buttons()
        self._status_label.setObjectName("StatusBadge")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)
        self._agent_label = label("")
        layout.addWidget(self._agent_label)
        form = form_layout()
        for caption, widget in (
            ("Bot", self._bot_combo),
            ("Kolor gracza", self._human_color_combo),
            ("Głębokość minimaxa", self._depth_spinbox),
        ):
            field_label = label(caption)
            field_label.setBuddy(widget)
            form.addRow(field_label, widget)
        configuration = QWidget()
        config_layout = QVBoxLayout(configuration)
        config_layout.setContentsMargins(8, 8, 8, 8)
        config_layout.addLayout(form)
        help_for(self._depth_spinbox, "depth")
        self._new_game_button.setObjectName("PrimaryButton")
        config_layout.addWidget(self._new_game_button)
        config_layout.addStretch()
        self._game_tabs = QTabWidget()
        configuration_scroll = QScrollArea()
        configuration_scroll.setWidgetResizable(True)
        configuration_scroll.setWidget(configuration)
        self._game_tabs.addTab(configuration_scroll, "Ustawienia gry")
        self._game_tabs.addTab(self._history_list, "Historia ruchów")
        self._history_list.setMinimumHeight(100)
        layout.addWidget(self._game_tabs, 1)
        finish = QWidget()
        finish_layout = QVBoxLayout(finish)
        finish_layout.setContentsMargins(0, 0, 0, 0)
        finish_layout.addWidget(self._finish_game_button)
        finish_layout.addWidget(self._clear_game_button)
        self._fen_label.setObjectName("FenLabel")
        self._fen_label.setWordWrap(True)
        self._fen_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        help_for(self._fen_label, "fen")
        finish_layout.addWidget(label("FEN"))
        finish_layout.addWidget(self._fen_label)
        layout.addWidget(Disclosure("Szczegóły techniczne", finish))
        actions = QHBoxLayout()
        resign_button = QPushButton("Poddaj partię")
        resign_button.setObjectName("DangerButton")
        resign_button.clicked.connect(self._resign)
        actions.addWidget(resign_button)
        back_button = QPushButton("Powrót do menu")
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)
        actions.addWidget(back_button)
        layout.addLayout(actions)
        return panel

    def _configure_bot_combo(self) -> None:
        self._bot_combo.addItem("RandomBot", BotKind.RANDOM.value)
        self._bot_combo.addItem("StaticMinimaxBot", BotKind.STATIC_MINIMAX.value)
        self._bot_combo.addItem("AdaptiveMinimaxBot", BotKind.ADAPTIVE_MINIMAX.value)

    def _configure_human_color_combo(self) -> None:
        self._human_color_combo.addItem("Białe", "white")
        self._human_color_combo.addItem("Czarne", "black")

    def _configure_depth_spinbox(self) -> None:
        self._depth_spinbox.setMinimum(1)
        self._depth_spinbox.setMaximum(4)
        self._depth_spinbox.setValue(1)

    def _configure_buttons(self) -> None:
        self._new_game_button.clicked.connect(self._start_new_game)

        self._finish_game_button.setObjectName("SecondaryButton")
        self._finish_game_button.clicked.connect(self._finish_current_game)

        self._clear_game_button.setObjectName("SecondaryButton")
        self._clear_game_button.clicked.connect(self.prepare_for_new_game)

    def _start_new_game(self) -> None:
        self._clear_selection()

        bot_kind = self._bot_combo.currentData()
        human_color_name = self._human_color_combo.currentData()
        depth = self._depth_spinbox.value()

        bot = create_bot_for_gui(
            bot_kind=bot_kind,
            depth=depth,
        )

        human_color = parse_human_color(human_color_name)

        self._session = HumanVsBotSession(
            bot=bot,
            human_color=human_color,
        )

        self._set_configuration_enabled(False)
        self._game_tabs.setCurrentIndex(1)
        self._finish_game_button.setEnabled(True)
        self._clear_game_button.setEnabled(True)

        if human_color == chess.WHITE:
            self._session.start()
            self._refresh_from_session()
        else:
            self._run(self._session.start)

    @property
    def thinking(self) -> bool:
        return self._worker is not None

    def _run(self, action: Callable[[], object]) -> None:
        if self.thinking:
            return
        self._error = ""
        self.setEnabled(False)
        self._status_label.setText(tr("Bot myśli…"))
        self._worker = CampaignWorker(action, self)
        self._worker.failed.connect(self._failed)
        self._worker.finished.connect(self._done)
        self._worker.start()

    def _failed(self, message: str) -> None:
        self._error = message

    def _done(self) -> None:
        if self._worker:
            self._worker.deleteLater()
        self._worker = None
        self.setEnabled(True)
        self._refresh_from_session()
        if self._error:
            self._status_label.setText(tr(self._error))
        elif self._session and self._session.is_game_over():
            self._show_finished_game_summary()

    def _resign(self) -> None:
        if self._session and not self.thinking and not self._session.is_game_over():
            self._session.resign()
            self._show_finished_game_summary()

    def _finish_current_game(self) -> None:
        """
        Kończy aktualną sesję aplikacyjnie i przechodzi do podsumowania.

        To nie oznacza mata ani remisu według reguł szachowych.
        Wynik zostanie zapisany jako '*', jeśli partia nie była formalnie zakończona.
        """
        if self._session is None:
            self._status_label.setText(tr("Brak aktywnej partii do podsumowania."))
            return

        summary = self._session.get_current_game_summary()
        self._on_game_finished(summary)

    def _on_board_square_clicked(self, square: int) -> None:
        if self.thinking:
            return
        if self._session is None:
            self._status_label.setText(tr("Najpierw kliknij „Nowa gra”."))
            return

        if self._session.is_game_over():
            self._status_label.setText(game_status(self._session.get_status_message()))
            self._clear_selection()
            return

        board = self._session.get_board_copy()

        if board.turn != self._session.human_color:
            self._status_label.setText(tr("To nie jest tura gracza."))
            self._clear_selection()
            return

        clicked_square = chess.Square(square)

        if self._selected_square is None:
            self._select_square_if_valid(
                board=board,
                square=clicked_square,
            )
            return

        if clicked_square == self._selected_square:
            self._clear_selection()
            self._status_label.setText(tr("Anulowano wybór figury."))
            return

        clicked_piece = board.piece_at(clicked_square)

        if (
            clicked_piece is not None
            and clicked_piece.color == self._session.human_color
        ):
            self._select_square_if_valid(
                board=board,
                square=clicked_square,
            )
            return

        self._try_play_selected_move(
            board=board,
            target_square=clicked_square,
        )

    def _select_square_if_valid(
        self,
        board: chess.Board,
        square: chess.Square,
    ) -> None:
        if self._session is None:
            return

        piece = board.piece_at(square)

        if piece is None:
            self._status_label.setText(tr("Kliknij własną figurę."))
            return

        if piece.color != self._session.human_color:
            self._status_label.setText(tr("To nie jest twoja figura."))
            return

        legal_targets = get_legal_target_squares(
            board=board,
            from_square=square,
        )

        if not legal_targets:
            self._status_label.setText(tr("Ta figura nie ma legalnych ruchów."))
            return

        self._selected_square = square
        self._board_widget.set_selected_square(square)
        self._board_widget.set_legal_target_squares(legal_targets)

        square_name = chess.square_name(square)
        self._status_label.setText(
            tr("Wybrano figurę na polu {square}.").format(square=square_name)
        )

    def _try_play_selected_move(
        self,
        board: chess.Board,
        target_square: chess.Square,
    ) -> None:
        if self._session is None or self._selected_square is None:
            return

        move_uci = build_uci_move_from_clicks(
            board=board,
            from_square=self._selected_square,
            to_square=target_square,
        )

        candidates = [
            m
            for m in board.legal_moves
            if m.from_square == self._selected_square and m.to_square == target_square
        ]
        if candidates and candidates[0].promotion:
            names = [tr(name) for name in ("Hetman", "Wieża", "Goniec", "Skoczek")]
            choice, accepted = QInputDialog.getItem(
                self, tr("Promocja"), tr("Wybierz figurę"), names, 0, False
            )
            if not accepted:
                return
            move_uci = move_uci[:4] + "qrbn"[names.index(choice)]
        session = self._session
        self._clear_selection()
        self._run(lambda: session.play_human_move_uci(move_uci))

    def _show_finished_game_summary(self) -> None:
        if self._session is None:
            return

        summary = self._session.get_game_summary()
        self._on_game_finished(summary)

    def _refresh_from_session(self) -> None:
        if self._session is None:
            return

        board = self._session.get_board_copy()

        self._board_widget.set_flipped(self._session.human_color == chess.BLACK)
        self._board_widget.set_board(board)

        self._status_label.setText(game_status(self._session.get_status_message()))
        self._fen_label.setText(tr(self._session.get_fen()))

        self._agent_label.setText(self._session.bot_name)
        self._agent_label.show()
        self._refresh_history()

    def _refresh_history(self) -> None:
        if self._session is None:
            self._history_list.clear()
            return

        self._history_list.clear()

        for index, move in enumerate(self._session.get_move_history(), start=1):
            color = "Białe" if move.color == chess.WHITE else "Czarne"
            player = "gracz" if move.player_type.value == "human" else "bot"

            self._history_list.addItem(
                f"{index:02d}. {tr(color)} {tr(player)}: {move.san}"
            )

    def _clear_selection(self) -> None:
        self._selected_square = None
        self._board_widget.clear_highlights()

    def _set_configuration_enabled(self, enabled: bool) -> None:
        self._bot_combo.setEnabled(enabled)
        self._human_color_combo.setEnabled(enabled)
        self._depth_spinbox.setEnabled(enabled)
        self._new_game_button.setEnabled(enabled)
