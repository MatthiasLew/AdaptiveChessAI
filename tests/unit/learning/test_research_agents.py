import chess
import pytest

from adaptive_chess.learning.agents import (
    KINDS,
    ResearchAgent,
    dot,
    initial_state,
    move_features,
)


def test_imitation_learns_human_move_preference_only():
    board, move = chess.Board(), chess.Move.from_uci("e2e4")
    agent = ResearchAgent(initial_state("imitation"), training=True)
    agent.observe_move(board, move, chess.WHITE, True)
    assert agent.snapshot()["updates"] == 0
    agent.observe_move(board, move, chess.WHITE, False)
    state = agent.snapshot()
    assert state["updates"] == 1
    assert dot(state["weights"], move_features(board, move)) > dot(
        state["weights"], move_features(board, chess.Move.from_uci("g1h3"))
    )
    frozen = ResearchAgent(state)
    frozen.observe_move(board, move, chess.WHITE, False)
    assert frozen.snapshot() == state


def test_td_terminal_reward_sign_and_frozen_end_game():
    board = chess.Board()
    win = ResearchAgent(initial_state("td"), training=True)
    loss = ResearchAgent(initial_state("td"), training=True)
    win.end_game(board, "1-0")
    loss.end_game(board, "0-1")
    assert win.snapshot()["weights"][-1] > 0
    assert loss.snapshot()["weights"][-1] < 0
    frozen = ResearchAgent(win.snapshot())
    frozen.end_game(board, "0-1")
    assert frozen.snapshot() == win.snapshot()


@pytest.mark.parametrize("kind", KINDS)
def test_search_is_reproducible_bounded_and_does_not_mutate_model(kind):
    agent = ResearchAgent(initial_state(kind), depth=2, nodes=30, seed=9)
    before = agent.snapshot()
    board = chess.Board()
    first = agent.choose_move(board)
    assert 0 < agent.nodes <= 30
    assert first == agent.choose_move(board)
    assert first in board.legal_moves
    assert board.fen() == chess.STARTING_FEN
    assert before == agent.snapshot()


def test_td_rule_terminal_is_learned_once():
    agent = ResearchAgent(initial_state("td"), training=True)
    board = chess.Board()
    for uci in ("f2f3", "e7e5", "g2g4"):
        board.push_uci(uci)
    agent.observe_move(board, chess.Move.from_uci("d8h4"), chess.BLACK, True)
    before = agent.snapshot()
    assert before["weights"] != [0.0] * 7
    board.push_uci("d8h4")
    agent.end_game(board, board.result())
    assert agent.snapshot() == before


@pytest.mark.parametrize("kind", KINDS)
def test_agents_choose_immediate_mate_with_full_root_budget(kind):
    board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 w - - 0 1")
    agent = ResearchAgent(initial_state(kind), depth=1, nodes=500)
    move = agent.choose_move(board)
    board.push(move)
    assert board.is_checkmate()


@pytest.mark.parametrize("bad_weight", [float("nan"), float("inf"), "wrong"])
def test_invalid_model_weights_are_rejected(bad_weight):
    state = initial_state("td")
    state["weights"][0] = bad_weight
    with pytest.raises(ValueError, match="model state"):
        ResearchAgent(state)


def test_td_draw_reward_moves_a_nonzero_prediction_toward_zero():
    state = initial_state("td")
    state["weights"][-1] = 0.5
    agent = ResearchAgent(state, training=True)
    agent.end_game(chess.Board(), "1/2-1/2")
    assert 0 < agent.snapshot()["weights"][-1] < 0.5
