import chess

from adaptive_chess.evaluation.position import evaluate_position


def _validate_perspective(perspective: chess.Color) -> None:
    """
    Sprawdza, czy perspektywa jest poprawnym kolorem szachowym.

    Args:
        perspective: Kolor do sprawdzenia.

    Raises:
        ValueError: Jeśli perspective nie jest chess.WHITE albo chess.BLACK.
    """
    if perspective not in (chess.WHITE, chess.BLACK):
        raise ValueError("perspective must be chess.WHITE or chess.BLACK.")


def minimax_score(
    board: chess.Board,
    depth: int,
    perspective: chess.Color,
) -> float:
    """
    Oblicza ocenę pozycji przy użyciu podstawowego algorytmu minimax.

    Args:
        board: Aktualna plansza.
        depth: Głębokość przeszukiwania.
        perspective: Kolor, z którego perspektywy oceniamy pozycję.

    Returns:
        Ocena pozycji z perspektywy podanego koloru.

    Raises:
        ValueError: Jeśli depth jest ujemne.
        ValueError: Jeśli perspective nie jest poprawnym kolorem.
    """
    if depth < 0:
        raise ValueError("depth must be greater than or equal to 0.")

    _validate_perspective(perspective)

    if depth == 0 or board.is_game_over():
        return evaluate_position(board, perspective)

    legal_moves = list(board.legal_moves)

    if board.turn == perspective:
        best_score = float("-inf")

        for move in legal_moves:
            board.push(move)
            score = minimax_score(board, depth - 1, perspective)
            board.pop()

            best_score = max(best_score, score)

        return best_score

    best_score = float("inf")

    for move in legal_moves:
        board.push(move)
        score = minimax_score(board, depth - 1, perspective)
        board.pop()

        best_score = min(best_score, score)

    return best_score


def alpha_beta_score(
    board: chess.Board,
    depth: int,
    perspective: chess.Color,
    alpha: float = float("-inf"),
    beta: float = float("inf"),
) -> float:
    """
    Oblicza ocenę pozycji przy użyciu minimaxa z alfa-beta pruning.

    Args:
        board: Aktualna plansza.
        depth: Głębokość przeszukiwania.
        perspective: Kolor, z którego perspektywy oceniamy pozycję.
        alpha: Najlepszy wynik znaleziony dotąd dla strony maksymalizującej.
        beta: Najlepszy wynik znaleziony dotąd dla strony minimalizującej.

    Returns:
        Ocena pozycji z perspektywy podanego koloru.

    Raises:
        ValueError: Jeśli depth jest ujemne.
        ValueError: Jeśli perspective nie jest poprawnym kolorem.
    """
    if depth < 0:
        raise ValueError("depth must be greater than or equal to 0.")

    _validate_perspective(perspective)

    if depth == 0 or board.is_game_over():
        return evaluate_position(board, perspective)

    legal_moves = list(board.legal_moves)

    if board.turn == perspective:
        best_score = float("-inf")

        for move in legal_moves:
            board.push(move)
            score = alpha_beta_score(
                board=board,
                depth=depth - 1,
                perspective=perspective,
                alpha=alpha,
                beta=beta,
            )
            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        return best_score

    best_score = float("inf")

    for move in legal_moves:
        board.push(move)
        score = alpha_beta_score(
            board=board,
            depth=depth - 1,
            perspective=perspective,
            alpha=alpha,
            beta=beta,
        )
        board.pop()

        best_score = min(best_score, score)
        beta = min(beta, best_score)

        if alpha >= beta:
            break

    return best_score


def find_best_move(
    board: chess.Board,
    depth: int,
    perspective: chess.Color,
) -> chess.Move:
    """
    Wybiera najlepszy ruch dla aktualnej pozycji przy użyciu podstawowego minimaxa.

    Args:
        board: Aktualna plansza.
        depth: Głębokość przeszukiwania.
        perspective: Kolor bota wybierającego ruch.

    Returns:
        Najlepszy znaleziony ruch.

    Raises:
        ValueError: Jeśli nie ma legalnych ruchów.
        ValueError: Jeśli depth jest mniejsze niż 1.
        ValueError: Jeśli perspective nie jest poprawnym kolorem.
        ValueError: Jeśli ruch ma wykonać inny kolor niż perspective.
    """
    if depth < 1:
        raise ValueError("depth must be at least 1 when choosing a move.")

    _validate_perspective(perspective)

    if board.turn != perspective:
        raise ValueError("board.turn must match perspective when choosing a move.")

    legal_moves = list(board.legal_moves)

    if not legal_moves:
        raise ValueError("Cannot choose a move because there are no legal moves.")

    best_move = legal_moves[0]
    best_score = float("-inf")

    for move in legal_moves:
        board.push(move)
        score = minimax_score(board, depth - 1, perspective)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def find_best_move_alpha_beta(
    board: chess.Board,
    depth: int,
    perspective: chess.Color,
) -> chess.Move:
    """
    Wybiera najlepszy ruch przy użyciu minimaxa z alfa-beta pruning.

    Args:
        board: Aktualna plansza.
        depth: Głębokość przeszukiwania.
        perspective: Kolor bota wybierającego ruch.

    Returns:
        Najlepszy znaleziony ruch.

    Raises:
        ValueError: Jeśli nie ma legalnych ruchów.
        ValueError: Jeśli depth jest mniejsze niż 1.
        ValueError: Jeśli perspective nie jest poprawnym kolorem.
        ValueError: Jeśli ruch ma wykonać inny kolor niż perspective.
    """
    if depth < 1:
        raise ValueError("depth must be at least 1 when choosing a move.")

    _validate_perspective(perspective)

    if board.turn != perspective:
        raise ValueError("board.turn must match perspective when choosing a move.")

    legal_moves = list(board.legal_moves)

    if not legal_moves:
        raise ValueError("Cannot choose a move because there are no legal moves.")

    best_move = legal_moves[0]
    best_score = float("-inf")
    alpha = float("-inf")
    beta = float("inf")

    for move in legal_moves:
        board.push(move)
        score = alpha_beta_score(
            board=board,
            depth=depth - 1,
            perspective=perspective,
            alpha=alpha,
            beta=beta,
        )
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move

        alpha = max(alpha, best_score)

    return best_move