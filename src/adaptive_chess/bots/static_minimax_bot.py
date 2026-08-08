import chess

from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.search.minimax import find_best_move


class StaticMinimaxBot(BaseBot):
    """
    Klasyczny bot szachowy oparty na algorytmie minimax.

    Bot analizuje możliwe ruchy do określonej głębokości i wybiera ruch,
    który prowadzi do najlepszej oceny pozycji z perspektywy strony,
    która aktualnie wykonuje ruch.

    Bot nie uczy się i nie zmienia swojego zachowania na podstawie historii partii.
    """

    def __init__(self, name: str = "StaticMinimaxBot", depth: int = 1) -> None:
        """
        Tworzy bota minimaxowego.

        Args:
            name: Nazwa bota.
            depth: Głębokość przeszukiwania minimax.

        Raises:
            ValueError: Jeśli depth jest mniejsze niż 1.
        """
        if depth < 1:
            raise ValueError("depth must be at least 1.")

        super().__init__(name)
        self.depth = depth

    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Wybiera najlepszy ruch dla aktualnej strony na ruchu.

        Args:
            board: Aktualna plansza.

        Returns:
            Najlepszy znaleziony ruch według minimaxa.

        Raises:
            ValueError: Jeśli nie ma legalnych ruchów.
        """
        board_copy = board.copy()
        perspective = board_copy.turn

        return find_best_move(
            board=board_copy,
            depth=self.depth,
            perspective=perspective,
        )