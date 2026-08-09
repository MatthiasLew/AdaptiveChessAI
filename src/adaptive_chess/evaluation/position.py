import chess

from adaptive_chess.evaluation.material import calculate_material_balance


CHECKMATE_SCORE = 10_000

MATERIAL_WEIGHT = 1.0
MOBILITY_WEIGHT = 0.05
CENTER_CONTROL_WEIGHT = 0.25

CENTER_SQUARES = (
    chess.D4,
    chess.E4,
    chess.D5,
    chess.E5,
)


def evaluate_position(
    board: chess.Board,
    perspective: chess.Color = chess.WHITE,
) -> float:
    """
    Ocenia aktualną pozycję szachową z perspektywy wybranego koloru.

    Wynik dodatni oznacza korzystną pozycję dla danego koloru.
    Wynik ujemny oznacza niekorzystną pozycję dla danego koloru.
    Wynik 0 oznacza pozycję ocenioną jako równą.

    Funkcja uwzględnia:
    - mata,
    - remisowe zakończenia,
    - przewagę materialną,
    - mobilność, czyli liczbę legalnych ruchów,
    - kontrolę centrum.

    Args:
        board: Aktualna plansza szachowa.
        perspective: Kolor, z którego perspektywy oceniana jest pozycja.

    Returns:
        Liczbowa ocena pozycji.
    """
    _validate_perspective(perspective)

    if board.is_checkmate():
        if board.turn == perspective:
            return -CHECKMATE_SCORE

        return CHECKMATE_SCORE

    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    material_score = calculate_material_balance(board, perspective)
    mobility_score = calculate_mobility_balance(board, perspective)
    center_control_score = calculate_center_control_balance(board, perspective)

    return (
        MATERIAL_WEIGHT * material_score
        + MOBILITY_WEIGHT * mobility_score
        + CENTER_CONTROL_WEIGHT * center_control_score
    )


def calculate_mobility_balance(
    board: chess.Board,
    perspective: chess.Color,
) -> int:
    """
    Liczy różnicę mobilności między stronami.

    Mobilność oznacza liczbę legalnych ruchów dostępnych dla danego koloru.
    Wynik dodatni oznacza większą mobilność koloru perspective.
    Wynik ujemny oznacza większą mobilność przeciwnika.

    Args:
        board: Aktualna plansza.
        perspective: Kolor, z którego perspektywy liczona jest mobilność.

    Returns:
        Różnica liczby legalnych ruchów.
    """
    _validate_perspective(perspective)

    opponent = not perspective

    perspective_mobility = _count_legal_moves_for_color(board, perspective)
    opponent_mobility = _count_legal_moves_for_color(board, opponent)

    return perspective_mobility - opponent_mobility


def calculate_center_control_balance(
    board: chess.Board,
    perspective: chess.Color,
) -> int:
    """
    Liczy różnicę kontroli centrum.

    Kontrola centrum jest liczona jako liczba ataków na pola:
    d4, e4, d5, e5.

    Args:
        board: Aktualna plansza.
        perspective: Kolor, z którego perspektywy liczona jest kontrola centrum.

    Returns:
        Różnica kontroli centrum.
    """
    _validate_perspective(perspective)

    opponent = not perspective

    perspective_control = _count_center_attacks(board, perspective)
    opponent_control = _count_center_attacks(board, opponent)

    return perspective_control - opponent_control


def _count_legal_moves_for_color(
    board: chess.Board,
    color: chess.Color,
) -> int:
    """
    Liczy legalne ruchy dla wskazanego koloru.

    python-chess liczy legalne ruchy dla strony zapisanej w board.turn,
    dlatego tutaj używamy kopii planszy i tymczasowo ustawiamy stronę na ruchu.
    """
    board_copy = board.copy(stack=False)
    board_copy.turn = color

    return len(list(board_copy.legal_moves))


def _count_center_attacks(
    board: chess.Board,
    color: chess.Color,
) -> int:
    """
    Liczy, ile figur danego koloru atakuje centralne pola.
    """
    attacks = 0

    for square in CENTER_SQUARES:
        attacks += len(board.attackers(color, square))

    return attacks


def _validate_perspective(perspective: chess.Color) -> None:
    """
    Sprawdza, czy perspektywa jest poprawnym kolorem szachowym.
    """
    if perspective not in (chess.WHITE, chess.BLACK):
        raise ValueError("Perspective must be chess.WHITE or chess.BLACK.")