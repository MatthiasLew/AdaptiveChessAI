import chess

from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.evaluation.position import calculate_center_control_balance


CENTER_RESPONSE_THRESHOLD = 0.30
CAPTURE_RESPONSE_THRESHOLD = 0.30
CHECK_RESPONSE_THRESHOLD = 0.15

CENTER_RESPONSE_WEIGHT = 0.10
PROTECTED_PIECE_BONUS = 0.25
OPPONENT_CHECK_PENALTY = 0.15


def calculate_adaptive_move_adjustment(
    board_after_move: chess.Board,
    move: chess.Move,
    perspective: chess.Color,
    opponent_profile: OpponentMoveProfile,
) -> float:
    """
    Oblicza adaptacyjną korektę oceny ruchu na podstawie profilu przeciwnika.

    Funkcja nie zastępuje minimaxa. Dodaje jedynie małą korektę do oceny ruchu,
    jeśli profil przeciwnika wskazuje konkretny styl gry.

    Uwzględniane cechy:
    - częste ruchy przeciwnika do centrum,
    - częste bicia przeciwnika,
    - częste szachy przeciwnika.

    Args:
        board_after_move: Plansza po wykonaniu analizowanego ruchu.
        move: Analizowany ruch.
        perspective: Kolor bota adaptacyjnego.
        opponent_profile: Profil przeciwnika zebrany podczas partii.

    Returns:
        Dodatnia lub ujemna korekta oceny ruchu.
    """
    if perspective not in (chess.WHITE, chess.BLACK):
        raise ValueError("perspective must be chess.WHITE or chess.BLACK.")

    adjustment = 0.0

    if opponent_profile.center_move_ratio >= CENTER_RESPONSE_THRESHOLD:
        adjustment += (
            CENTER_RESPONSE_WEIGHT
            * calculate_center_control_balance(board_after_move, perspective)
        )

    if opponent_profile.capture_ratio >= CAPTURE_RESPONSE_THRESHOLD:
        if _moved_piece_is_protected(
            board_after_move=board_after_move,
            move=move,
            perspective=perspective,
        ):
            adjustment += PROTECTED_PIECE_BONUS

    if opponent_profile.check_ratio >= CHECK_RESPONSE_THRESHOLD:
        opponent = not perspective
        opponent_checking_moves = _count_checking_moves_for_color(
            board=board_after_move,
            color=opponent,
        )
        adjustment -= OPPONENT_CHECK_PENALTY * opponent_checking_moves

    return adjustment


def _moved_piece_is_protected(
    board_after_move: chess.Board,
    move: chess.Move,
    perspective: chess.Color,
) -> bool:
    """
    Sprawdza, czy figura po wykonanym ruchu jest broniona przez własną figurę.

    Args:
        board_after_move: Plansza po ruchu.
        move: Wykonany ruch.
        perspective: Kolor bota.

    Returns:
        True, jeśli figura na polu docelowym jest broniona.
    """
    piece = board_after_move.piece_at(move.to_square)

    if piece is None or piece.color != perspective:
        return False

    defenders = board_after_move.attackers(perspective, move.to_square)

    return len(defenders) > 0


def _count_checking_moves_for_color(
    board: chess.Board,
    color: chess.Color,
) -> int:
    """
    Liczy, ile legalnych ruchów danego koloru dawałoby szacha.

    Args:
        board: Aktualna plansza.
        color: Kolor, dla którego liczymy ruchy szachujące.

    Returns:
        Liczba legalnych ruchów dających szacha.
    """
    board_copy = board.copy(stack=False)
    board_copy.turn = color

    checking_moves = 0

    for move in list(board_copy.legal_moves):
        board_copy.push(move)

        if board_copy.is_check():
            checking_moves += 1

        board_copy.pop()

    return checking_moves