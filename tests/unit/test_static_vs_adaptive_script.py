from argparse import Namespace

import pytest

from scripts.run_static_vs_adaptive_series import (
    build_experiment_metadata,
    validate_experiment_config,
)


def test_validate_experiment_config_accepts_valid_values():
    validate_experiment_config(
        matches_count=1,
        max_half_moves=1,
        depths=[1],
        adjudication_material_threshold=3,
    )


def test_validate_experiment_config_rejects_zero_matches():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=0,
            max_half_moves=1,
            depths=[1],
            adjudication_material_threshold=3,
        )


def test_validate_experiment_config_rejects_zero_max_half_moves():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=0,
            depths=[1],
            adjudication_material_threshold=3,
        )


def test_validate_experiment_config_rejects_empty_depths():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=1,
            depths=[],
            adjudication_material_threshold=3,
        )


def test_validate_experiment_config_rejects_invalid_depth():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=1,
            depths=[1, 0],
            adjudication_material_threshold=3,
        )


def test_validate_experiment_config_rejects_invalid_adjudication_threshold():
    with pytest.raises(ValueError):
        validate_experiment_config(
            matches_count=1,
            max_half_moves=1,
            depths=[1],
            adjudication_material_threshold=0,
        )


def test_build_experiment_metadata_includes_adaptive_profile_snapshots():
    args = Namespace(
        matches=2,
        max_half_moves=20,
        depths=[1],
        adjudication_material_threshold=3,
        output_csv="results/test.csv",
    )

    profile_snapshots = [
        {
            "series_name": (
                "StaticMinimaxBot-White-depth-1 "
                "vs AdaptiveMinimaxBot-Black-depth-1"
            ),
            "adaptive_bot_color": "black",
            "opponent_bot": "StaticMinimaxBot",
            "depth": 1,
            "profile": {
                "observed_moves": 10,
                "captures": 2,
                "checks": 1,
                "center_moves": 3,
                "capture_ratio": 0.2,
                "check_ratio": 0.1,
                "center_move_ratio": 0.3,
            },
        }
    ]

    metadata = build_experiment_metadata(
        args=args,
        adaptive_profile_snapshots=profile_snapshots,
    )

    assert metadata["adaptive_profile_scope"] == "series_persistent"
    assert metadata["adaptive_profile_snapshots"] == profile_snapshots