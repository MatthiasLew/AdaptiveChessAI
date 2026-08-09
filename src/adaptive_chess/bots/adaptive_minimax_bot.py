import chess

from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.search.minimax import find_best_move_alpha_beta


class AdaptiveMinimaxBot(BaseBot):
    """
    Pierwsza wersja bota adaptacyjnego.

    Bot wybiera ruchy za pomocą minimaxa z alfa-beta pruning,
    a dodatkowo obserwuje ruchy przeciwnika i zapisuje prosty profil jego stylu.

    Wersja v1 skupia się na zbieraniu danych o przeciwniku.
    W kolejnej wersji profil będzie używany do modyfikowania decyzji bota.
    """

    def __init__(self, name: str = "AdaptiveMinimaxBot", depth: int = 1) -> None:
        """
        Tworzy adaptacyjnego bota minimaxowego.

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
        self.opponent_profile = OpponentMoveProfile()

    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Wybiera ruch przy użyciu minimaxa z alfa-beta pruning.

        Args:
            board: Aktualna plansza.

        Returns:
            Najlepszy znaleziony ruch.
        """
        board_copy = board.copy()
        perspective = board_copy.turn

        return find_best_move_alpha_beta(
            board=board_copy,
            depth=self.depth,
            perspective=perspective,
        )

    def observe_move(
        self,
        board_before_move: chess.Board,
        move: chess.Move,
        played_by: chess.Color,
        is_own_move: bool,
    ) -> None:
        """
        Obserwuje ruchy przeciwnika i aktualizuje profil.

        Ruchy własne są ignorowane, bo profil ma opisywać przeciwnika.

        Args:
            board_before_move: Plansza przed ruchem.
            move: Wykonany ruch.
            played_by: Kolor, który wykonał ruch.
            is_own_move: True, jeśli ruch wykonał ten bot.
        """
        if is_own_move:
            return

        self.opponent_profile.observe_move(
            board_before_move=board_before_move,
            move=move,
        )