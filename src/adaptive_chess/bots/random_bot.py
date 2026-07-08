import random

import chess

from src.adaptive_chess.bots.base_bot import BaseBot


class RandomBot(BaseBot):
    """
    Bot wybierający losowy ruch spośród wszystkich legalnych ruchów.

    RandomBot pełni rolę punktu odniesienia dla bardziej zaawansowanych botów.
    Nie analizuje pozycji i nie uczy się na podstawie historii partii.
    """

    def __init__(self, name: str = "RandomBot") -> None:
        """
        Tworzy bota losowego.

        Args:
            name: Nazwa bota używana później w wynikach, statystykach i turniejach.
        """
        super().__init__(name)

    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Wybiera losowy legalny ruch z aktualnej pozycji.

        Args:
            board: Aktualna plansza szachowa.

        Returns:
            Losowo wybrany legalny ruch.

        Raises:
            ValueError: Jeśli dla danej pozycji nie ma legalnych ruchów.
        """
        legal_moves = list(board.legal_moves)

        if not legal_moves:
            raise ValueError("Cannot choose a move because there are no legal moves.")

        return random.choice(legal_moves)