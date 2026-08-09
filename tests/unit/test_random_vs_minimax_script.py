import pytest

from scripts.run_random_vs_minimax_series import validate_experiment_config


def test_validate_experiment_config_accepts_valid_values():
    validate_experiment_config(
        matches_count=1,
        max_half_moves=1,
        depths=[1],
    )


def test_validate_experiment_config_rejects_zero_matches():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=0,
            max_half_moves=1,
            depths=[1],
        )


def test_validate_experiment_config_rejects_zero_max_half_moves():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=0,
            depths=[1],
        )


def test_validate_experiment_config_rejects_empty_depths():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=1,
            depths=[],
        )


def test_validate_experiment_config_rejects_invalid_depth():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=1,
            depths=[1, 0],
        )