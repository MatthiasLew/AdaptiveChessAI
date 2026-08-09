import chess

from adaptive_chess.adaptation.adaptive_scoring import (
    calculate_adaptive_move_adjustment,
)
from adaptive_chess.adaptation.opponent_profile import OpponentMoveProfile
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.search.minimax import alpha_beta_score


ADAPTIVE_BOT_VERSION = "profile_adjusted_move_scoring_v1"


class AdaptiveMinimaxBot(BaseBot):
    """
    Bot adaptacyjny oparty na minimaxie z alfa-beta pruning.

    Bot obserwuje ruchy przeciwnika, buduje prosty profil jego stylu
    i wykorzystuje ten profil jako dodatkową korektę przy wyborze ruchu.

    Profil przeciwnika może być własny dla pojedynczego bota albo współdzielony
    między botami tworzonymi w kolejnych partiach tej samej serii.
    """

    def __init__(
        self,
        name: str = "AdaptiveMinimaxBot",
        depth: int = 1,
        opponent_profile: OpponentMoveProfile | None = None,
    ) -> None:
        """
        Tworzy adaptacyjnego bota minimaxowego.

        Args:
            name: Nazwa bota.
            depth: Głębokość przeszukiwania minimax.
            opponent_profile: Opcjonalny współdzielony profil przeciwnika.

        Raises:
            ValueError: Jeśli depth jest mniejsze niż 1.
        """
        if depth < 1:
            raise ValueError("depth must be at least 1.")

        super().__init__(name)
        self.depth = depth
        self.opponent_profile = (
            opponent_profile if opponent_profile is not None else OpponentMoveProfile()
        )

    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Wybiera ruch przy użyciu minimaxa i adaptacyjnej korekty profilu przeciwnika.

        Args:
            board: Aktualna plansza.

        Returns:
            Najlepszy znaleziony ruch.
        """
        board_copy = board.copy()
        perspective = board_copy.turn
        legal_moves = list(board_copy.legal_moves)

        if not legal_moves:
            raise ValueError("Cannot choose a move because there are no legal moves.")

        best_move = legal_moves[0]
        best_score = float("-inf")

        for move in legal_moves:
            board_copy.push(move)

            base_score = alpha_beta_score(
                board=board_copy,
                depth=self.depth - 1,
                perspective=perspective,
            )

            adaptive_adjustment = calculate_adaptive_move_adjustment(
                board_after_move=board_copy,
                move=move,
                perspective=perspective,
                opponent_profile=self.opponent_profile,
            )

            total_score = base_score + adaptive_adjustment

            board_copy.pop()

            if total_score > best_score:
                best_score = total_score
                best_move = move

        return best_move

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