from dataclasses import dataclass

import chess


CENTER_SQUARES = {
    chess.D4,
    chess.E4,
    chess.D5,
    chess.E5,
}


@dataclass
class OpponentMoveProfile:
    """
    Prosty profil zachowania przeciwnika.

    Profil zlicza podstawowe cechy ruchów przeciwnika:
    - liczbę zaobserwowanych ruchów,
    - liczbę bić,
    - liczbę szachów,
    - liczbę ruchów na centralne pola.
    """

    observed_moves: int = 0
    captures: int = 0
    checks: int = 0
    center_moves: int = 0

    def observe_move(
        self,
        board_before_move: chess.Board,
        move: chess.Move,
    ) -> None:
        """
        Aktualizuje profil na podstawie jednego ruchu przeciwnika.

        Args:
            board_before_move: Plansza przed wykonaniem ruchu.
            move: Ruch przeciwnika.

        Raises:
            ValueError: Jeśli ruch nie jest legalny w podanej pozycji.
        """
        if move not in board_before_move.legal_moves:
            raise ValueError(f"Cannot observe illegal move: {move}")

        self.observed_moves += 1

        if board_before_move.is_capture(move):
            self.captures += 1

        if move.to_square in CENTER_SQUARES:
            self.center_moves += 1

        board_after_move = board_before_move.copy(stack=False)
        board_after_move.push(move)

        if board_after_move.is_check():
            self.checks += 1

    @property
    def capture_ratio(self) -> float:
        """
        Zwraca udział ruchów będących biciami.
        """
        return self._safe_ratio(self.captures)

    @property
    def check_ratio(self) -> float:
        """
        Zwraca udział ruchów dających szacha.
        """
        return self._safe_ratio(self.checks)

    @property
    def center_move_ratio(self) -> float:
        """
        Zwraca udział ruchów kończących się na centralnych polach.
        """
        return self._safe_ratio(self.center_moves)

    def to_dict(self) -> dict[str, int | float]:
        """
        Zwraca profil w formie słownika.

        Przydatne do debugowania, metadanych oraz przyszłego eksportu profili.
        """
        return {
            "observed_moves": self.observed_moves,
            "captures": self.captures,
            "checks": self.checks,
            "center_moves": self.center_moves,
            "capture_ratio": self.capture_ratio,
            "check_ratio": self.check_ratio,
            "center_move_ratio": self.center_move_ratio,
        }

    def _safe_ratio(self, value: int) -> float:
        if self.observed_moves == 0:
            return 0.0

        return value / self.observed_moves