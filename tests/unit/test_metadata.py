import json

import pytest

from adaptive_chess.experiments.metadata import (
    resolve_metadata_output_path,
    write_experiment_metadata,
)


def test_resolve_metadata_output_path_uses_explicit_metadata_path(tmp_path):
    csv_path = tmp_path / "results.csv"
    metadata_path = tmp_path / "custom.json"

    resolved_path = resolve_metadata_output_path(
        output_csv_path=csv_path,
        output_metadata_path=metadata_path,
    )

    assert resolved_path == metadata_path


def test_resolve_metadata_output_path_uses_csv_sidecar_path(tmp_path):
    csv_path = tmp_path / "results.csv"

    resolved_path = resolve_metadata_output_path(
        output_csv_path=csv_path,
        output_metadata_path=None,
    )

    assert resolved_path == tmp_path / "results.metadata.json"


def test_resolve_metadata_output_path_rejects_missing_paths():
    with pytest.raises(ValueError):
        resolve_metadata_output_path(
            output_csv_path=None,
            output_metadata_path=None,
        )


def test_write_experiment_metadata_creates_json_file(tmp_path):
    output_path = tmp_path / "metadata.json"

    saved_path = write_experiment_metadata(
        metadata={
            "experiment_type": "test",
            "matches_count": 5,
            "position_evaluation_version": "test-version",
        },
        output_path=output_path,
    )

    assert saved_path == output_path
    assert output_path.exists()

    loaded_metadata = json.loads(output_path.read_text(encoding="utf-8"))

    assert loaded_metadata["experiment_type"] == "test"
    assert loaded_metadata["matches_count"] == 5
    assert loaded_metadata["position_evaluation_version"] == "test-version"
    assert "generated_at_utc" in loaded_metadata