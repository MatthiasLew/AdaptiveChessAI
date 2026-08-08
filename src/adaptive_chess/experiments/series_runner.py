from collections.abc import Callable

from adaptive_chess.bots.base_bot import BaseBot
from adaptive_chess.experiments.match_runner import MatchResult, MatchRunner


class SeriesRunner:
    """
    Uruchamia serię partii między dwoma typami botów.

    SeriesRunner wykorzystuje MatchRunner do rozgrywania pojedynczych partii.
    Jego zadaniem jest powtórzenie meczu określoną liczbę razy
    i zwrócenie kolekcji wyników.
    """

    def __init__(
        self,
        matches_count: int,
        max_half_moves: int = 200,
        initial_fen: str | None = None,
    ) -> None:
        """
        Tworzy runner serii partii.

        Args:
            matches_count: Liczba partii do rozegrania.
            max_half_moves: Maksymalna liczba półruchów w jednej partii.
            initial_fen: Opcjonalna pozycja startowa dla każdej partii.

        Raises:
            ValueError: Jeśli liczba partii jest mniejsza niż 1.
            ValueError: Jeśli limit półruchów jest mniejszy niż 1.
        """
        if matches_count < 1:
            raise ValueError("matches_count must be at least 1.")

        if max_half_moves < 1:
            raise ValueError("max_half_moves must be at least 1.")

        self.matches_count = matches_count
        self.max_half_moves = max_half_moves
        self.initial_fen = initial_fen

    def play_series(
        self,
        white_bot_factory: Callable[[], BaseBot],
        black_bot_factory: Callable[[], BaseBot],
    ) -> tuple[MatchResult, ...]:
        """
        Rozgrywa serię partii między botami tworzonymi przez podane fabryki.

        Args:
            white_bot_factory: Funkcja tworząca bota grającego białymi.
            black_bot_factory: Funkcja tworząca bota grającego czarnymi.

        Returns:
            Niemodyfikowalna kolekcja wyników partii.
        """
        results: list[MatchResult] = []

        for _ in range(self.matches_count):
            white_bot = white_bot_factory()
            black_bot = black_bot_factory()

            match_runner = MatchRunner(
                max_half_moves=self.max_half_moves,
                initial_fen=self.initial_fen,
            )

            result = match_runner.play(white_bot, black_bot)
            results.append(result)

        return tuple(results)