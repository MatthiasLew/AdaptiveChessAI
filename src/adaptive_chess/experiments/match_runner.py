from dataclasses import dataclass
from enum import Enum

import chess

from adaptive_chess.experiments.adjudication import adjudicate_result_by_material
from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.core.game import Game
from adaptive_chess.evaluation.material import calculate_material_balance
from adaptive_chess.evaluation.position import evaluate_position


class TerminationReason(Enum):
    """
    Powód zakończenia partii.

    RULES oznacza, że partia zakończyła się zgodnie z zasadami szachów,
    np. matem, patem albo remisem wykrytym przez python-chess.

    MOVE_LIMIT oznacza, że partia została zatrzymana przez sztuczny limit
    półruchów ustawiony w MatchRunner.
    """

    RULES = "rules"
    MOVE_LIMIT = "move_limit"


@dataclass(frozen=True)
class MatchResult:
    """
    Wynik pojedynczej partii między dwoma botami.

    Obiekt przechowuje podstawowe informacje potrzebne później
    do statystyk, turniejów oraz zapisu wyników do bazy danych.
    """

    white_bot_name: str
    black_bot_name: str
    result: str
    adjudicated_result: str
    termination_reason: TerminationReason
    half_moves: int
    moves_uci: tuple[str, ...]
    material_balances: tuple[int, ...]
    position_scores: tuple[float, ...]
    final_material_balance: int
    final_fen: str
    reached_move_limit: bool


class MatchRunner:
    """
    Uruchamia pojedynczą partię szachową między dwoma botami.

    MatchRunner nie implementuje logiki szachowej samodzielnie.
    Do obsługi planszy używa klasy Game, a do wyboru ruchów używa botów.
    """

    def __init__(self, max_half_moves: int = 200, initial_fen: str | None = None, adjudication_material_threshold: int = 3,) -> None:
        """
        Tworzy runner do rozgrywania partii.

        Args:
            max_half_moves: Maksymalna liczba półruchów w partii.
                            Jeden półruch to jeden ruch jednego gracza.
            initial_fen: Opcjonalna pozycja startowa w formacie FEN.

        Raises:
            ValueError: Jeśli limit półruchów jest mniejszy niż 1.
        """
        if max_half_moves < 1:
            raise ValueError("max_half_moves must be at least 1.")
        if adjudication_material_threshold < 1:
            raise ValueError("adjudication_material_threshold must be at least 1.")
        self.max_half_moves = max_half_moves
        self.initial_fen = initial_fen
        self.adjudication_material_threshold = adjudication_material_threshold

    def play(self, white_bot: BaseBot, black_bot: BaseBot) -> MatchResult:
        """
        Rozgrywa partię między białym i czarnym botem.

        Args:
            white_bot: Bot grający białymi.
            black_bot: Bot grający czarnymi.

        Returns:
            Obiekt MatchResult z wynikiem partii.
        """
        game = Game(self.initial_fen)
        half_moves = 0

        moves_uci: list[str] = []
        material_balances: list[int] = []
        position_scores: list[float] = []

        while not game.is_game_over() and half_moves < self.max_half_moves:
            current_bot = white_bot if game.get_turn() == chess.WHITE else black_bot

            board_copy = game.get_board_copy()
            move = current_bot.choose_move(board_copy)

            game.make_move(move)
            half_moves += 1

            current_board = game.get_board_copy()

            moves_uci.append(move.uci())
            material_balances.append(
                calculate_material_balance(current_board, chess.WHITE)
            )
            position_scores.append(
                evaluate_position(current_board, chess.WHITE)
            )

        reached_move_limit = not game.is_game_over()

        final_board = game.get_board_copy()
        final_material_balance = calculate_material_balance(final_board, chess.WHITE)

        if reached_move_limit:
            termination_reason = TerminationReason.MOVE_LIMIT
            result = "1/2-1/2"
            adjudicated_result = adjudicate_result_by_material(
                final_material_balance=final_material_balance,
                material_threshold=self.adjudication_material_threshold,
            )
        else:
            termination_reason = TerminationReason.RULES
            result = game.get_result()
            if result is None:
                result = "1/2-1/2"

            adjudicated_result = result
        return MatchResult(
            white_bot_name=white_bot.name,
            black_bot_name=black_bot.name,
            result=result,
            termination_reason=termination_reason,
            half_moves=half_moves,
            moves_uci=tuple(moves_uci),
            material_balances=tuple(material_balances),
            position_scores=tuple(position_scores),
            final_material_balance=final_material_balance,
            final_fen=game.get_fen(),
            reached_move_limit=reached_move_limit,
            adjudicated_result=adjudicated_result,
        )