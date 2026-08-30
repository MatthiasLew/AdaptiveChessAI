import chess

from PySide6.QtCore import Qt
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
    """
    Zamienia figurę python-chess na znak Unicode.

    Args:
        piece: Figura z biblioteki python-chess albo None.

    Returns:
        Znak Unicode figury albo pusty tekst.
    """
    if piece is None:
        return ""

    return PIECE_UNICODE_SYMBOLS[piece.symbol()]


def square_to_grid_position(
    square: chess.Square,
    flipped: bool = False,
) -> tuple[int, int]:
    """
    Zamienia pole szachowe na pozycję w siatce GUI.

    Args:
        square: Pole python-chess.
        flipped: Czy plansza jest odwrócona dla gry czarnymi.

    Returns:
        Para (row, column).
    """
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)

    if flipped:
        return rank_index, 7 - file_index

    return 7 - rank_index, file_index


def is_light_square(square: chess.Square) -> bool:
    """
    Sprawdza, czy pole jest jasne.
    """
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)

    return (file_index + rank_index) % 2 == 1


class ChessBoardWidget(QFrame):
    """
    Prosty widget szachownicy.

    Na tym etapie widget tylko wyświetla pozycję.
    Klikanie pól zostanie dodane w kolejnym etapie.
    """

    def __init__(self) -> None:
        super().__init__()

        self._board = chess.Board()
        self._flipped = False
        self._square_labels: dict[chess.Square, QLabel] = {}

        self.setObjectName("BoardFrame")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._layout = QGridLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._layout)

        self._build_squares()
        self.set_board(self._board)

    def set_board(self, board: chess.Board) -> None:
        """
        Ustawia pozycję wyświetlaną na szachownicy.
        """
        self._board = board.copy(stack=False)
        self._refresh_pieces()

    def set_flipped(self, flipped: bool) -> None:
        """
        Odwraca orientację planszy.
        """
        if self._flipped == flipped:
            return

        self._flipped = flipped
        self._rebuild_squares()
        self._refresh_pieces()

    def _build_squares(self) -> None:
        for square in chess.SQUARES:
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumSize(62, 62)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            font = label.font()
            font.setPointSize(28)
            label.setFont(font)

            if is_light_square(square):
                label.setObjectName("BoardLightSquare")
            else:
                label.setObjectName("BoardDarkSquare")

            row, column = square_to_grid_position(
                square=square,
                flipped=self._flipped,
            )

            self._layout.addWidget(label, row, column)
            self._square_labels[square] = label

    def _rebuild_squares(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self._square_labels.clear()
        self._build_squares()

    def _refresh_pieces(self) -> None:
        for square, label in self._square_labels.items():
            piece = self._board.piece_at(square)
            label.setText(piece_to_unicode(piece))