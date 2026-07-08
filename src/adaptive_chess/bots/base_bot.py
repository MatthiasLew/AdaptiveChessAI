from abc import ABC, abstractmethod

import chess


class BaseBot(ABC):
    """
    Bazowa klasa abstrakcyjna dla wszystkich botów szachowych.

    Każdy bot w projekcie powinien dziedziczyć po tej klasie
    i zaimplementować metodę choose_move().
    """

    def __init__(self, name: str) -> None:
        """
        Tworzy bota o podanej nazwie.

        Args:
            name: Nazwa bota, np. "RandomBot" albo "StaticMinimaxBot".
        """
        self.name = name

    @abstractmethod
    def choose_move(self, board: chess.Board) -> chess.Move:
        """
        Wybiera ruch dla aktualnej pozycji na planszy.

        Args:
            board: Aktualny stan planszy z biblioteki python-chess.

        Returns:
            Wybrany legalny ruch typu chess.Move.
        """
        raise NotImplementedError