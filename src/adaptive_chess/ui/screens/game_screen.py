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
from adaptive_chess.ui.widgets.chess_board_widget import ChessBoardWidget


class GameScreen(QWidget):
    """
    Ekran gry z botem.

    Ten ekran posiada już układ pod właściwą rozgrywkę:
    szachownicę, wybór bota, wybór koloru, depth, historię i status.

    Klikanie pól zostanie dodane w kolejnym etapie.
    """

    def __init__(
        self,
        on_back_to_menu_clicked: Callable[[], None],
    ) -> None:
        super().__init__()

        self._on_back_to_menu_clicked = on_back_to_menu_clicked
        self._session: HumanVsBotSession | None = None

        self._board_widget = ChessBoardWidget()

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
            "Ruchy kliknięciami zostaną dodane w następnym etapie. "
            "Na razie ekran pokazuje konfigurację gry i aktualną planszę."
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
            self._history_list.addItem(
                f"{index:02d}. {color} {move.player_type.value}: "
                f"{move.san} ({move.move_uci})"
            )