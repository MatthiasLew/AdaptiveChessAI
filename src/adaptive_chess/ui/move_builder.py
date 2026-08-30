import chess


def build_uci_move_from_clicks(
    board: chess.Board,
    from_square: chess.Square,
    to_square: chess.Square,
) -> str:
    """
    Buduje ruch UCI na podstawie kliknięcia pola źródłowego i docelowego.

    Dla zwykłych ruchów zwraca np. e2e4.
    Dla promocji piona domyślnie wybiera hetmana, np. e7e8q.
    """
    regular_move = chess.Move(
        from_square=from_square,
        to_square=to_square,
    )

    if regular_move in board.legal_moves:
        return regular_move.uci()

    promotion_move = _try_build_promotion_move(
        board=board,
        from_square=from_square,
        to_square=to_square,
    )

    if promotion_move is not None:
        return promotion_move.uci()

    return regular_move.uci()


def _try_build_promotion_move(
    board: chess.Board,
    from_square: chess.Square,
    to_square: chess.Square,
) -> chess.Move | None:
    piece = board.piece_at(from_square)

    if piece is None or piece.piece_type != chess.PAWN:
        return None

    target_rank = chess.square_rank(to_square)

    if target_rank not in (0, 7):
        return None

    for promotion_piece in (
        chess.QUEEN,
        chess.ROOK,
        chess.BISHOP,
        chess.KNIGHT,
    ):
        move = chess.Move(
            from_square=from_square,
            to_square=to_square,
            promotion=promotion_piece,
        )

        if move in board.legal_moves:
            return move

    return None


def get_legal_target_squares(
    board: chess.Board,
    from_square: chess.Square,
) -> tuple[chess.Square, ...]:
    """
    Zwraca pola docelowe legalnych ruchów z wybranego pola.
    """
    return tuple(
        move.to_square for move in board.legal_moves if move.from_square == from_square
    )
