from dataclasses import dataclass
from enum import Enum

import chess

from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.core.game import Game


class PlayerType(str, Enum):
    """
    Typ gracza wykonującego ruch.
    """

    HUMAN = "human"
    BOT = "bot"


@dataclass(frozen=True)
class PlayedMove:
    """
    Informacja o wykonanym ruchu w sesji człowiek vs bot.
    """

    player_type: PlayerType
    color: chess.Color
    move_uci: str
    san: str


@dataclass(frozen=True)
class HumanMoveResult:
    """
    Wynik próby wykonania ruchu człowieka.

    Jeśli ruch człowieka był legalny, `human_move` zawiera wykonany ruch.
    Jeśli po ruchu człowieka bot mógł odpowiedzieć, `bot_move` zawiera odpowiedź bota.
    """

    human_move: PlayedMove
    bot_move: PlayedMove | None
    is_game_over: bool
    result: str | None
    status_message: str


class HumanVsBotSession:
    """
    Kontroluje pojedynczą partię człowiek vs bot.

    Ta klasa jest warstwą pośrednią między przyszłym GUI a logiką gry.
    GUI nie powinno bezpośrednio zarządzać zasadami szachów ani odpowiedzią bota.
    Zamiast tego powinno korzystać z tej klasy.
    """

    def __init__(
        self,
        bot: BaseBot,
        human_color: chess.Color = chess.WHITE,
        initial_fen: str | None = None,
    ) -> None:
        """
        Tworzy sesję człowiek vs bot.

        Args:
            bot: Bot, przeciwko któremu gra człowiek.
            human_color: Kolor człowieka.
            initial_fen: Opcjonalna pozycja startowa.

        Raises:
            ValueError: Jeśli human_color nie jest poprawnym kolorem.
        """
        if human_color not in (chess.WHITE, chess.BLACK):
            raise ValueError("human_color must be chess.WHITE or chess.BLACK.")

        self._game = Game(initial_fen)
        self._bot = bot
        self._human_color = human_color
        self._bot_color = not human_color
        self._moves: list[PlayedMove] = []
        self._started = False

    @property
    def human_color(self) -> chess.Color:
        return self._human_color

    @property
    def bot_color(self) -> chess.Color:
        return self._bot_color

    @property
    def bot_name(self) -> str:
        return self._bot.name

    def start(self) -> PlayedMove | None:
        """
        Rozpoczyna sesję.

        Jeśli człowiek gra czarnymi, bot wykonuje pierwszy ruch.
        Jeśli człowiek gra białymi, metoda nie wykonuje ruchu.

        Returns:
            Ruch bota, jeśli bot zaczyna partię. W przeciwnym razie None.

        Raises:
            RuntimeError: Jeśli sesja została już rozpoczęta.
        """
        if self._started:
            raise RuntimeError("Session has already started.")

        self._started = True

        if self.is_game_over():
            return None

        if self.get_turn() == self._bot_color:
            return self._play_bot_move()

        return None

    def play_human_move_uci(self, move_uci: str) -> HumanMoveResult:
        """
        Wykonuje ruch człowieka zapisany w notacji UCI.

        Przykłady:
        - e2e4
        - g1f3
        - e7e8q

        Args:
            move_uci: Ruch w notacji UCI.

        Returns:
            Wynik ruchu człowieka i opcjonalnej odpowiedzi bota.

        Raises:
            RuntimeError: Jeśli sesja nie została rozpoczęta.
            RuntimeError: Jeśli gra już się zakończyła.
            RuntimeError: Jeśli nie jest tura człowieka.
            ValueError: Jeśli UCI jest niepoprawne albo ruch jest nielegalny.
        """
        if not self._started:
            raise RuntimeError("Session must be started before playing moves.")

        if self.is_game_over():
            raise RuntimeError("Cannot play move because the game is over.")

        if self.get_turn() != self._human_color:
            raise RuntimeError("It is not the human player's turn.")

        human_move = self._parse_legal_human_move(move_uci)
        played_human_move = self._push_move(
            player_type=PlayerType.HUMAN,
            move=human_move,
        )

        if self.is_game_over():
            return HumanMoveResult(
                human_move=played_human_move,
                bot_move=None,
                is_game_over=True,
                result=self.get_result(),
                status_message=self.get_status_message(),
            )

        played_bot_move = self._play_bot_move()

        return HumanMoveResult(
            human_move=played_human_move,
            bot_move=played_bot_move,
            is_game_over=self.is_game_over(),
            result=self.get_result(),
            status_message=self.get_status_message(),
        )

    def get_board_copy(self) -> chess.Board:
        """
        Zwraca kopię aktualnej planszy.
        """
        return self._game.get_board_copy()

    def get_fen(self) -> str:
        """
        Zwraca aktualny FEN.
        """
        return self._game.get_fen()

    def get_turn(self) -> chess.Color:
        """
        Zwraca kolor, który ma teraz ruch.
        """
        return self._game.get_turn()

    def get_legal_moves_uci(self) -> tuple[str, ...]:
        """
        Zwraca legalne ruchy w notacji UCI.
        """
        return tuple(move.uci() for move in self._game.get_legal_moves())

    def get_move_history(self) -> tuple[PlayedMove, ...]:
        """
        Zwraca historię ruchów wykonanych w sesji.
        """
        return tuple(self._moves)

    def is_game_over(self) -> bool:
        """
        Sprawdza, czy partia się zakończyła.
        """
        return self._game.is_game_over()

    def get_result(self) -> str | None:
        """
        Zwraca wynik partii albo None, jeśli partia trwa.
        """
        return self._game.get_result()

    def get_status_message(self) -> str:
        """
        Zwraca czytelny opis aktualnego stanu gry.

        Ten tekst może być później wyświetlany w GUI.
        """
        board = self._game.get_board_copy()

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            return f"Checkmate. Winner: {winner}."

        if board.is_stalemate():
            return "Draw by stalemate."

        if board.is_insufficient_material():
            return "Draw by insufficient material."

        if board.is_game_over():
            result = board.result()
            return f"Game over. Result: {result}."

        turn = "White" if board.turn == chess.WHITE else "Black"

        if board.is_check():
            return f"{turn} to move. Check."

        return f"{turn} to move."

    def _parse_legal_human_move(self, move_uci: str) -> chess.Move:
        """
        Parsuje i sprawdza legalność ruchu człowieka.
        """
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError as error:
            raise ValueError(f"Invalid UCI move: {move_uci}") from error

        legal_moves = self._game.get_legal_moves()

        if move not in legal_moves:
            raise ValueError(f"Illegal move: {move_uci}")

        return move

    def _play_bot_move(self) -> PlayedMove:
        """
        Wybiera i wykonuje ruch bota.

        Returns:
            Informacja o wykonanym ruchu bota.

        Raises:
            RuntimeError: Jeśli nie jest tura bota.
            ValueError: Jeśli bot zwróci nielegalny ruch.
        """
        if self.get_turn() != self._bot_color:
            raise RuntimeError("It is not the bot's turn.")

        board_before_move = self._game.get_board_copy()
        move = self._bot.choose_move(board_before_move.copy())

        if move not in board_before_move.legal_moves:
            raise ValueError(f"Bot returned illegal move: {move}")

        return self._push_move(
            player_type=PlayerType.BOT,
            move=move,
        )

    def _push_move(
        self,
        player_type: PlayerType,
        move: chess.Move,
    ) -> PlayedMove:
        """
        Wykonuje ruch i zapisuje go w historii.
        """
        board_before_move = self._game.get_board_copy()
        color = board_before_move.turn
        san = board_before_move.san(move)

        self._game.make_move(move)

        played_move = PlayedMove(
            player_type=player_type,
            color=color,
            move_uci=move.uci(),
            san=san,
        )

        self._moves.append(played_move)

        return played_move