import chess
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QSizePolicy,
)

PIECE_UNICODE_SYMBOLS: dict[str, str] = {
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}


def piece_to_unicode(piece: chess.Piece | None) -> str:
    if piece is None:
        return ""

    return PIECE_UNICODE_SYMBOLS[piece.symbol()]


def square_to_grid_position(
    square: chess.Square,
    flipped: bool = False,
) -> tuple[int, int]:
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)

    if flipped:
        return rank_index, 7 - file_index

    return 7 - rank_index, file_index


def is_light_square(square: chess.Square) -> bool:
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)

    return (file_index + rank_index) % 2 == 1


class BoardSquareLabel(QLabel):
    """
    Pojedyncze klikalne pole szachownicy.
    """

    clicked = Signal(int)

    def __init__(self, square: chess.Square) -> None:
        super().__init__()
        self.square = square
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.square)
        super().mousePressEvent(event)


class ChessBoardWidget(QFrame):
    """
    Widget szachownicy.

    Wyświetla pozycję, obsługuje kliknięcia pól oraz proste podświetlenia:
    - wybrane pole,
    - legalne pola docelowe.
    """

    square_clicked = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        self._board = chess.Board()
        self._flipped = False
        self._selected_square: chess.Square | None = None
        self._legal_target_squares: set[chess.Square] = set()
        self._square_labels: dict[chess.Square, BoardSquareLabel] = {}

        self.setObjectName("BoardFrame")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._layout = QGridLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._layout)

        self._build_squares()
        self.set_board(self._board)

    def set_board(self, board: chess.Board) -> None:
        self._board = board.copy(stack=False)
        self._refresh_pieces()
        self._refresh_square_styles()

    def set_flipped(self, flipped: bool) -> None:
        if self._flipped == flipped:
            return

        self._flipped = flipped
        self._rebuild_squares()
        self._refresh_pieces()
        self._refresh_square_styles()

    def set_selected_square(self, square: chess.Square | None) -> None:
        self._selected_square = square
        self._refresh_square_styles()

    def set_legal_target_squares(
        self,
        squares: tuple[chess.Square, ...],
    ) -> None:
        self._legal_target_squares = set(squares)
        self._refresh_square_styles()

    def clear_highlights(self) -> None:
        self._selected_square = None
        self._legal_target_squares.clear()
        self._refresh_square_styles()

    def _build_squares(self) -> None:
        for square in chess.SQUARES:
            label = BoardSquareLabel(square)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumSize(62, 62)
            label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )

            font = label.font()
            font.setPointSize(28)
            label.setFont(font)

            label.clicked.connect(self.square_clicked.emit)

            row, column = square_to_grid_position(
                square=square,
                flipped=self._flipped,
            )

            self._layout.addWidget(label, row, column)
            self._square_labels[square] = label

    def _rebuild_squares(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                continue

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self._square_labels.clear()
        self._build_squares()

    def _refresh_pieces(self) -> None:
        for square, label in self._square_labels.items():
            piece = self._board.piece_at(square)
            label.setText(piece_to_unicode(piece))

    def _refresh_square_styles(self) -> None:
        for square, label in self._square_labels.items():
            label.setObjectName(self._get_square_object_name(square))
            label.style().unpolish(label)
            label.style().polish(label)

    def _get_square_object_name(self, square: chess.Square) -> str:
        if square == self._selected_square:
            return "BoardSelectedSquare"

        if square in self._legal_target_squares:
            return "BoardLegalTargetSquare"

        if is_light_square(square):
            return "BoardLightSquare"

        return "BoardDarkSquare"
