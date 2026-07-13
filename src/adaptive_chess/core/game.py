import chess


class Game:
    """
    Reprezentuje pojedynczą partię szachową.

    Klasa opakowuje obiekt chess.Board z biblioteki python-chess
    i udostępnia kontrolowany interfejs do wykonywania ruchów,
    sprawdzania stanu gry oraz pobierania aktualnej pozycji.
    """

    def __init__(self, fen: str | None = None) -> None:
        """
        Tworzy nową partię.

        Args:
            fen: Opcjonalny zapis pozycji w formacie FEN.
                 Jeśli nie zostanie podany, tworzona jest standardowa pozycja startowa.
        """
        self._board = chess.Board(fen) if fen is not None else chess.Board()

    def get_board_copy(self) -> chess.Board:
        """
        Zwraca kopię aktualnej planszy.

        Returns:
            Kopia obiektu chess.Board.
        """
        return self._board.copy()

    def get_fen(self) -> str:
        """
        Zwraca aktualną pozycję w formacie FEN.

        Returns:
            Tekstowy zapis aktualnego stanu planszy.
        """
        return self._board.fen()

    def get_turn(self) -> chess.Color:
        """
        Zwraca kolor gracza, który ma wykonać ruch.

        Returns:
            chess.WHITE albo chess.BLACK.
        """
        return self._board.turn

    def get_legal_moves(self) -> list[chess.Move]:
        """
        Zwraca listę legalnych ruchów w aktualnej pozycji.

        Returns:
            Lista legalnych ruchów.
        """
        return list(self._board.legal_moves)

    def make_move(self, move: chess.Move) -> None:
        """
        Wykonuje legalny ruch na planszy.

        Args:
            move: Ruch typu chess.Move.

        Raises:
            ValueError: Jeśli ruch nie jest legalny w aktualnej pozycji.
        """
        if move not in self._board.legal_moves:
            raise ValueError(f"Illegal move: {move}")

        self._board.push(move)

    def make_move_uci(self, move_uci: str) -> None:
        """
        Wykonuje ruch zapisany w formacie UCI, np. 'e2e4'.

        Args:
            move_uci: Ruch w formacie UCI.

        Raises:
            ValueError: Jeśli zapis ruchu jest błędny albo ruch jest nielegalny.
        """
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError as error:
            raise ValueError(f"Invalid UCI move: {move_uci}") from error

        self.make_move(move)

    def is_game_over(self) -> bool:
        """
        Sprawdza, czy partia jest zakończona.

        Returns:
            True, jeśli partia jest zakończona. W przeciwnym razie False.
        """
        return self._board.is_game_over()

    def get_result(self) -> str | None:
        """
        Zwraca wynik partii, jeśli partia jest zakończona.

        Returns:
            '1-0' dla wygranej białych,
            '0-1' dla wygranej czarnych,
            '1/2-1/2' dla remisu,
            None, jeśli partia jeszcze trwa.
        """
        if not self.is_game_over():
            return None

        return self._board.result()