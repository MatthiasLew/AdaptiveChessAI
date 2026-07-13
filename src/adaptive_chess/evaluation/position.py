import chess

from src.adaptive_chess.evaluation.material import calculate_material_balance


CHECKMATE_SCORE = 10_000


def evaluate_position(
    board: chess.Board,
    perspective: chess.Color = chess.WHITE,
) -> float:
    """
    Ocenia aktualną pozycję szachową z perspektywy wybranego koloru.

    Wynik dodatni oznacza korzystną pozycję dla danego koloru.
    Wynik ujemny oznacza niekorzystną pozycję dla danego koloru.
    Wynik 0 oznacza pozycję ocenioną jako równą.

    Na tym etapie funkcja uwzględnia:
    - mata,
    - remisowe zakończenia,
    - przewagę materialną.

    Args:
        board: Aktualna plansza szachowa.
        perspective: Kolor, z którego perspektywy oceniana jest pozycja.

    Returns:
        Liczbowa ocena pozycji.
    """
    if perspective not in (chess.WHITE, chess.BLACK):
        raise ValueError("Perspective must be chess.WHITE or chess.BLACK.")

    if board.is_checkmate():
        if board.turn == perspective:
            return -CHECKMATE_SCORE

        return CHECKMATE_SCORE

    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    return float(calculate_material_balance(board, perspective))