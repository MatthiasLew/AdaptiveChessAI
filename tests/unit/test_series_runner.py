import pytest

from adaptive_chess.bots.random_bot import RandomBot
from adaptive_chess.experiments.series_runner import SeriesRunner


def test_series_runner_plays_requested_number_of_matches():
    runner = SeriesRunner(matches_count=5, max_half_moves=2)

    results = runner.play_series(
        white_bot_factory=lambda: RandomBot("RandomWhite"),
        black_bot_factory=lambda: RandomBot("RandomBlack"),
    )

    assert len(results) == 5
    assert all(result.white_bot_name == "RandomWhite" for result in results)
    assert all(result.black_bot_name == "RandomBlack" for result in results)
    assert all(result.half_moves <= 2 for result in results)


def test_series_runner_returns_tuple_of_results():
    runner = SeriesRunner(matches_count=3, max_half_moves=1)

    results = runner.play_series(
        white_bot_factory=lambda: RandomBot("RandomWhite"),
        black_bot_factory=lambda: RandomBot("RandomBlack"),
    )

    assert isinstance(results, tuple)
    assert len(results) == 3


def test_series_runner_uses_bot_factories_for_each_match():
    created_white_bots = 0
    created_black_bots = 0

    def create_white_bot() -> RandomBot:
        nonlocal created_white_bots
        created_white_bots += 1
        return RandomBot(f"RandomWhite-{created_white_bots}")

    def create_black_bot() -> RandomBot:
        nonlocal created_black_bots
        created_black_bots += 1
        return RandomBot(f"RandomBlack-{created_black_bots}")

    runner = SeriesRunner(matches_count=4, max_half_moves=1)

    results = runner.play_series(
        white_bot_factory=create_white_bot,
        black_bot_factory=create_black_bot,
    )

    assert created_white_bots == 4
    assert created_black_bots == 4
    assert results[0].white_bot_name == "RandomWhite-1"
    assert results[-1].white_bot_name == "RandomWhite-4"


def test_series_runner_rejects_invalid_matches_count():
    with pytest.raises(ValueError):
        SeriesRunner(matches_count=0)


def test_series_runner_rejects_invalid_max_half_moves():
    with pytest.raises(ValueError):
        SeriesRunner(matches_count=1, max_half_moves=0)