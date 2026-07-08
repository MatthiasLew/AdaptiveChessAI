import chess


PIECE_VALUES: dict[chess.PieceType, int] = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}


def calculate_material(board: chess.Board, color: chess.Color) -> int:
    """
    Liczy wartość materialną figur danego koloru.

    Args:
        board: Aktualna plansza szachowa.
        color: Kolor, dla którego liczony jest materiał.
               chess.WHITE oznacza białe, chess.BLACK oznacza czarne.

    Returns:
        Suma wartości figur danego koloru.
    """
    if color not in (chess.WHITE, chess.BLACK):
        raise ValueError("Color must be chess.WHITE or chess.BLACK.")

    material = 0

    for piece_type, piece_value in PIECE_VALUES.items():
        pieces = board.pieces(piece_type, color)
        material += len(pieces) * piece_value

    return material


def calculate_material_balance(
    board: chess.Board,
    perspective: chess.Color = chess.WHITE,
) -> int:
    """
    Liczy przewagę materialną z perspektywy wybranego koloru.

    Wynik dodatni oznacza przewagę wybranego koloru.
    Wynik ujemny oznacza stratę materialną wybranego koloru.
    Wynik 0 oznacza równowagę materialną.

    Args:
        board: Aktualna plansza szachowa.
        perspective: Kolor, z którego perspektywy liczona jest przewaga.

    Returns:
        Różnica materiału z perspektywy podanego koloru.
    """
    if perspective not in (chess.WHITE, chess.BLACK):
        raise ValueError("Perspective must be chess.WHITE or chess.BLACK.")

    white_material = calculate_material(board, chess.WHITE)
    black_material = calculate_material(board, chess.BLACK)

    if perspective == chess.WHITE:
        return white_material - black_material

    return black_material - white_material