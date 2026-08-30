from collections.abc import Callable

import chess

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from adaptive_chess.play.human_vs_bot_session import HumanVsBotSession
from adaptive_chess.ui.bot_factory import (
    BotKind,
    create_bot_for_gui,
    parse_human_color,
)
from adaptive_chess.ui.move_builder import (
    build_uci_move_from_clicks,
    get_legal_target_squares,
)
from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget


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
    - status gry.
    """

    def __init__(
        self,
        on_back_to_menu_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._session: HumanVsBotSession | None = None
        self._selected_square: chess.Square | None = None

        self._board_widget = ChessBoardWidget()
        self._board_widget.square_clicked.connect(self._on_board_square_clicked)

        self._bot_combo = QComboBox()
        self._human_color_combo = QComboBox()
        self._depth_spinbox = QSpinBox()

        self._status_label = QLabel("Nie rozpoczęto gry.")
        self._fen_label = QLabel("-")
        self._history_list = QListWidget()

        self._build_ui()
        self._initialize_default_board()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(30, 30, 30, 30)
        root_layout.setSpacing(16)

        title = QLabel("Gra z botem")
        title.setObjectName("SectionTitle")

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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(self._board_widget, stretch=1)

        hint = QLabel(
            "Kliknij własną figurę, a potem pole docelowe. "
            "Po ruchu człowieka bot odpowie automatycznie."
        )
        hint.setObjectName("SubtitleLabel")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)

        layout.addWidget(hint)
        panel.setLayout(layout)

        return panel

    def _build_side_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        settings_title = QLabel("Ustawienia gry")
        settings_title.setObjectName("SectionTitle")

        self._configure_bot_combo()
        self._configure_human_color_combo()
        self._configure_depth_spinbox()

        new_game_button = QPushButton("Nowa gra")
        new_game_button.clicked.connect(self._start_new_game)

        back_button = QPushButton("Powrót do menu")
        back_button.setObjectName("SecondaryButton")
        back_button.clicked.connect(self._on_back_to_menu_clicked)

        self._status_label.setObjectName("StatusLabel")
        self._status_label.setWordWrap(True)

        fen_title = QLabel("FEN")
        self._fen_label.setObjectName("FenLabel")
        self._fen_label.setWordWrap(True)

        history_title = QLabel("Historia ruchów")

        layout.addWidget(settings_title)
        layout.addWidget(QLabel("Bot"))
        layout.addWidget(self._bot_combo)
        layout.addWidget(QLabel("Kolor gracza"))
        layout.addWidget(self._human_color_combo)
        layout.addWidget(QLabel("Głębokość minimaxa"))
        layout.addWidget(self._depth_spinbox)
        layout.addWidget(new_game_button)
        layout.addWidget(back_button)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Status"))
        layout.addWidget(self._status_label)
        layout.addWidget(fen_title)
        layout.addWidget(self._fen_label)
        layout.addWidget(history_title)
        layout.addWidget(self._history_list, stretch=1)

        panel.setLayout(layout)

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

    def _initialize_default_board(self) -> None:
        board = chess.Board()
        self._board_widget.set_board(board)
        self._board_widget.set_flipped(False)
        self._fen_label.setText(board.fen())

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

        opening_bot_move = self._session.start()

        self._refresh_from_session()

        if opening_bot_move is not None:
            self._status_label.setText(
                f"Bot rozpoczął partię ruchem: "
                f"{opening_bot_move.san} ({opening_bot_move.move_uci})"
            )

    def _on_board_square_clicked(self, square: int) -> None:
        if self._session is None:
            self._status_label.setText("Najpierw kliknij „Nowa gra”.")
            return

        if self._session.is_game_over():
            self._status_label.setText(self._session.get_status_message())
            self._clear_selection()
            return

        board = self._session.get_board_copy()

        if board.turn != self._session.human_color:
            self._status_label.setText("To nie jest tura gracza.")
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
            self._status_label.setText("Anulowano wybór figury.")
            return

        clicked_piece = board.piece_at(clicked_square)

        if clicked_piece is not None and clicked_piece.color == self._session.human_color:
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
            self._status_label.setText("Kliknij własną figurę.")
            return

        if piece.color != self._session.human_color:
            self._status_label.setText("To nie jest twoja figura.")
            return

        legal_targets = get_legal_target_squares(
            board=board,
            from_square=square,
        )

        if not legal_targets:
            self._status_label.setText("Ta figura nie ma legalnych ruchów.")
            return

        self._selected_square = square
        self._board_widget.set_selected_square(square)
        self._board_widget.set_legal_target_squares(legal_targets)

        square_name = chess.square_name(square)
        self._status_label.setText(f"Wybrano figurę na polu {square_name}.")

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

        try:
            result = self._session.play_human_move_uci(move_uci)
        except (RuntimeError, ValueError) as error:
            self._status_label.setText(str(error))
            self._clear_selection()
            return

        self._clear_selection()
        self._refresh_from_session()

        if result.bot_move is not None:
            self._status_label.setText(
                f"Twój ruch: {result.human_move.san}. "
                f"Bot: {result.bot_move.san}. "
                f"{result.status_message}"
            )
        else:
            self._status_label.setText(
                f"Twój ruch: {result.human_move.san}. "
                f"{result.status_message}"
            )

    def _refresh_from_session(self) -> None:
        if self._session is None:
            return

        board = self._session.get_board_copy()

        self._board_widget.set_flipped(self._session.human_color == chess.BLACK)
        self._board_widget.set_board(board)

        self._status_label.setText(self._session.get_status_message())
        self._fen_label.setText(self._session.get_fen())

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
                f"{index:02d}. {color} {player}: "
                f"{move.san} ({move.move_uci})"
            )

    def _clear_selection(self) -> None:
        self._selected_square = None
        self._board_widget.clear_highlights()