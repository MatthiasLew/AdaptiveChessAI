from argparse import Namespace

import pytest

from scripts.run_full_experiment_suite import (
    build_analysis_commands,
    build_experiment_commands,
    validate_suite_config,
)


def create_args(
    skip_random_series: bool = False,
    skip_reports: bool = False,
    skip_charts: bool = False,
) -> Namespace:
    return Namespace(
        output_dir="results/full_suite",
        matches=2,
        max_half_moves=20,
        depths=[1],
        adjudication_material_threshold=3,
        skip_random_series=skip_random_series,
        skip_reports=skip_reports,
        skip_charts=skip_charts,
    )


def test_validate_suite_config_accepts_valid_values():
    validate_suite_config(
        matches_count=1,
        max_half_moves=1,
        depths=[1],
        adjudication_material_threshold=3,
    )


def test_validate_suite_config_rejects_zero_matches():
    with pytest.raises(ValueError):
        validate_suite_config(
            matches_count=0,
            max_half_moves=1,
            depths=[1],
            adjudication_material_threshold=3,
        )


def test_validate_suite_config_rejects_zero_max_half_moves():
    with pytest.raises(ValueError):
        validate_suite_config(
            matches_count=1,
            max_half_moves=0,
            depths=[1],
            adjudication_material_threshold=3,
        )


def test_validate_suite_config_rejects_empty_depths():
    with pytest.raises(ValueError):
        validate_suite_config(
            matches_count=1,
            max_half_moves=1,
            depths=[],
            adjudication_material_threshold=3,
        )


def test_validate_suite_config_rejects_invalid_depth():
    with pytest.raises(ValueError):
        validate_suite_config(
            matches_count=1,
            max_half_moves=1,
            depths=[1, 0],
            adjudication_material_threshold=3,
        )


def test_validate_suite_config_rejects_invalid_adjudication_threshold():
    with pytest.raises(ValueError):
        validate_suite_config(
            matches_count=1,
            max_half_moves=1,
            depths=[1],
            adjudication_material_threshold=0,
        )


def test_build_experiment_commands_includes_all_experiments_by_default():
    args = create_args()

    commands = build_experiment_commands(args)
    command_names = [command.name for command in commands]

    assert command_names == [
        "random_series",
        "random_vs_minimax",
        "random_vs_adaptive",
        "static_vs_adaptive",
    ]


def test_build_experiment_commands_can_skip_random_series():
    args = create_args(skip_random_series=True)

    commands = build_experiment_commands(args)
    command_names = [command.name for command in commands]

    assert command_names == [
        "random_vs_minimax",
        "random_vs_adaptive",
        "static_vs_adaptive",
    ]


def test_build_analysis_commands_includes_reports_and_charts_by_default():
    args = create_args()

    commands = build_analysis_commands(args)
    command_names = [command.name for command in commands]

    assert "report_random_series" in command_names
    assert "charts_random_series" in command_names
    assert "report_random_vs_minimax" in command_names
    assert "charts_random_vs_minimax" in command_names
    assert "report_random_vs_adaptive" in command_names
    assert "charts_random_vs_adaptive" in command_names
    assert "report_static_vs_adaptive" in command_names
    assert "charts_static_vs_adaptive" in command_names


def test_build_analysis_commands_can_skip_reports():
    args = create_args(skip_reports=True)

    commands = build_analysis_commands(args)
    command_names = [command.name for command in commands]

    assert all(not name.startswith("report_") for name in command_names)
    assert any(name.startswith("charts_") for name in command_names)


def test_build_analysis_commands_can_skip_charts():
    args = create_args(skip_charts=True)

    commands = build_analysis_commands(args)
    command_names = [command.name for command in commands]

    assert any(name.startswith("report_") for name in command_names)
    assert all(not name.startswith("charts_") for name in command_names)