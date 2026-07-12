from __future__ import annotations

import csv
import hashlib
import inspect
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from paper1.scripts.build_external_acpc_horizon_v2_artifact import (
    build_parser as build_external_atr_parser,
)
from paper1.scripts.build_external_smpr_v2_artifact import (
    build_parser as build_external_smpr_parser,
)
from paper1.scripts.build_frozen_diagnostic_input import (
    ROW_FIELDS,
    build_diagnostic_input,
    build_parser as build_diagnostic_parser,
)
from paper1.scripts.frozen_external_validation import (
    BLIND_FIELDS,
    _auprc,
    score_heldout,
)


PROTOCOL_PATH = ROOT / "paper1/config/frozen_diagnostic_protocol_v1.json"
EXTERNAL_ROOT = ROOT / "paper1/results/remediation_phase2_external_sources"
DIAGNOSTIC_PATH = (
    ROOT / "paper1/results/external_validation/lewm_heldout_diagnostic_input_v4.json"
)
BLIND_PATH = ROOT / "paper1/results/frozen_external_predictions_blind_v3.csv"
BLIND_SIDECAR_PATH = Path(f"{BLIND_PATH}.metadata.json")
SCORED_ROWS_PATH = ROOT / "paper1/results/frozen_external_validation_rows_v3.csv"
SCORE_SUMMARY_PATH = ROOT / "paper1/results/frozen_external_validation_summary_v3.json"
EVAL_MANIFESTS = (
    ROOT / "assets/paper1_data/training_seed_eval_manifests/lewm_seed3073_evals.json",
    ROOT / "assets/paper1_data/training_seed_eval_manifests/lewm_seed3074_evals.json",
)
TASKS = ("TwoRoom", "PushT", "Reacher", "Cube")
RHO_GRID = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08)
EXPECTED_GRID = {(task, rho) for task in TASKS for rho in RHO_GRID}
BEHAVIOR_FIELD_PARTS = (
    "behavior",
    "success",
    "score",
    "label",
    "return",
    "recovery",
    "ground_truth",
    "pixels",
)


def _strict_json(path: Path) -> dict[str, Any]:
    payload = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )
    assert isinstance(payload, dict)
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def _assert_live_path_hashes(
    paths: Mapping[str, str], hashes: Mapping[str, str]
) -> None:
    assert set(paths) == set(hashes)
    for key, value in paths.items():
        path = _repo_path(value)
        assert path.is_file(), f"missing provenance source {key}: {path}"
        assert _sha256(path) == hashes[key], f"stale provenance hash for {key}"


def _assert_behavior_free_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        for field in row:
            lowered = field.lower()
            assert not any(part in lowered for part in BEHAVIOR_FIELD_PARTS), field


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        return list(reader.fieldnames or ()), rows


def _csv_bool(value: str) -> bool:
    assert value in {"true", "false"}
    return value == "true"


def test_frozen_protocol_has_exactly_eight_live_source_hashes() -> None:
    protocol = _strict_json(PROTOCOL_PATH)
    expected = {
        "calibration_atr",
        "calibration_evals",
        "calibration_smpr",
        "canonical_metric",
        "freeze_builder",
        "protocol_schema",
        "semantic_margin",
        "smpr_runner",
    }

    assert set(protocol["source_paths"]) == expected
    assert set(protocol["source_hashes"]) == expected
    assert len(protocol["source_hashes"]) == 8
    _assert_live_path_hashes(protocol["source_paths"], protocol["source_hashes"])


@pytest.mark.parametrize(
    ("seed", "filename", "role", "schema"),
    (
        (3073, "acpc_horizon_v2_checkpoint_bound.json", "heldout_external_atr", "paper1-acpc-horizon-v2-1.0"),
        (3074, "acpc_horizon_v2_checkpoint_bound.json", "heldout_external_atr", "paper1-acpc-horizon-v2-1.0"),
        (3073, "smpr_v2_checkpoint_bound.json", "heldout_external_smpr", "paper1-smpr-v2-merged-1.0"),
        (3074, "smpr_v2_checkpoint_bound.json", "heldout_external_smpr", "paper1-smpr-v2-merged-1.0"),
    ),
)
def test_heldout_merged_artifacts_are_complete_behavior_blind_test_grids(
    seed: int, filename: str, role: str, schema: str
) -> None:
    path = EXTERNAL_ROOT / f"lewm_seed{seed}" / filename
    payload = _strict_json(path)
    metadata = payload["metadata"]
    rows = payload["rows"]
    protocol_sha = _sha256(PROTOCOL_PATH)

    assert metadata["schema_version"] == schema
    assert metadata["artifact_role"] == role
    assert metadata["status"] == "complete"
    assert metadata["status_counts"] == {"ok": 36}
    assert metadata["missing_rows"] == []
    assert metadata["errors"] == []
    assert metadata["behavior_blind"] is True
    assert metadata["split_name"] == "TEST"
    assert metadata["training_seed"] == seed
    assert metadata["training_family_id"] == f"lewm_seed{seed}"
    assert metadata["protocol_sha256"] == protocol_sha
    assert metadata["protocol_hash"] == protocol_sha
    assert len(rows) == 36
    assert {(row["task"], row["training_rho"]) for row in rows} == EXPECTED_GRID
    assert {row["status"] for row in rows} == {"ok"}
    assert {row["split_name"] for row in rows} == {"TEST"}
    assert {row["model_family"] for row in rows} == {"LeWM"}
    assert {row["training_seed"] for row in rows} == {seed}
    assert {row["training_family_id"] for row in rows} == {f"lewm_seed{seed}"}
    assert all(Path(row["model_file"]).is_file() for row in rows)
    assert all(
        _sha256(Path(row["model_file"])) == row["checkpoint_sha256"]
        for row in rows
    )
    _assert_behavior_free_rows(rows)

    _assert_live_path_hashes(metadata["source_paths"], metadata["source_hashes"])
    _assert_live_path_hashes(
        metadata["implementation_paths"], metadata["implementation_hashes"]
    )
    assert _sha256(_repo_path(metadata["script_path"])) == metadata["script_sha256"]
    assert (
        _sha256(_repo_path(metadata["base_builder_path"]))
        == metadata["base_builder_sha256"]
    )


def test_diagnostic_join_is_exactly_72_allowlisted_behavior_free_rows() -> None:
    artifact = _strict_json(DIAGNOSTIC_PATH)
    metadata = artifact["metadata"]
    rows = artifact["rows"]
    atr_paths = [
        EXTERNAL_ROOT / f"lewm_seed{seed}/acpc_horizon_v2_checkpoint_bound.json"
        for seed in (3073, 3074)
    ]
    smpr_paths = [
        EXTERNAL_ROOT / f"lewm_seed{seed}/smpr_v2_checkpoint_bound.json"
        for seed in (3073, 3074)
    ]

    assert len(rows) == 72
    assert metadata["status"] == "complete"
    assert metadata["status_counts"] == {"ok": 72}
    assert metadata["missing_rows"] == []
    assert metadata["errors"] == []
    assert metadata["behavior_blind"] is True
    assert metadata["threshold_search_available"] is False
    assert metadata["strict_external_contract"] == "lewm_heldout_gaussian_v1"
    assert metadata["split_name"] == "TEST"
    assert metadata["training_seeds"] == [3073, 3074]
    assert metadata["protocol_sha256"] == _sha256(PROTOCOL_PATH)
    assert all(set(row) == set(ROW_FIELDS) for row in rows)
    assert {row["split_name"] for row in rows} == {"TEST"}
    assert {row["status"] for row in rows} == {"ok"}
    assert {
        (row["training_seed"], row["task"], row["training_rho"])
        for row in rows
    } == {
        (seed, task, rho)
        for seed in (3073, 3074)
        for task, rho in EXPECTED_GRID
    }
    _assert_behavior_free_rows(rows)
    _assert_live_path_hashes(metadata["source_paths"], metadata["source_hashes"])
    assert _sha256(_repo_path(metadata["script_path"])) == metadata["script_sha256"]
    assert not any("eval" in key.lower() for key in metadata["source_paths"])

    rebuilt = build_diagnostic_input(
        protocol_path=PROTOCOL_PATH,
        atr_paths=atr_paths,
        smpr_paths=smpr_paths,
    )
    assert rebuilt["rows"] == rows
    assert rebuilt["metadata"]["source_hashes"] == metadata["source_hashes"]


def test_blind_prediction_sidecar_binds_rows_hash_and_count() -> None:
    sidecar = _strict_json(BLIND_SIDECAR_PATH)
    metadata = sidecar["metadata"]
    fields, rows = _read_csv(BLIND_PATH)
    protocol_sha = _sha256(PROTOCOL_PATH)
    diagnostics_sha = _sha256(DIAGNOSTIC_PATH)

    assert fields == list(BLIND_FIELDS)
    assert sidecar["fields"] == list(BLIND_FIELDS)
    assert sidecar["row_count"] == len(rows) == 72
    assert metadata["status"] == "complete"
    assert metadata["status_counts"] == {"ok": 72}
    assert metadata["behavior_blind"] is True
    assert metadata["threshold_search_available"] is False
    assert metadata["protocol_hash"] == protocol_sha
    assert metadata["source_hashes"]["blind_rows"] == _sha256(BLIND_PATH)
    assert metadata["source_hashes"]["diagnostics"] == diagnostics_sha
    _assert_live_path_hashes(metadata["source_paths"], metadata["source_hashes"])
    assert {row["split_name"] for row in rows} == {"TEST"}
    assert {row["protocol_sha256"] for row in rows} == {protocol_sha}
    assert {row["diagnostics_sha256"] for row in rows} == {diagnostics_sha}


def test_score_summary_sources_and_confusion_are_reproducible(
    tmp_path: Path,
) -> None:
    stored = _strict_json(SCORE_SUMMARY_PATH)
    metadata = stored["metadata"]
    _, scored_rows = _read_csv(SCORED_ROWS_PATH)

    assert set(metadata["source_paths"]) == set(metadata["source_hashes"])
    assert {
        "protocol",
        "predictions",
        "predictions_sidecar",
        "diagnostics",
        "lewm_seed3073",
        "lewm_seed3074",
    } <= set(metadata["source_paths"])
    assert len(
        [key for key in metadata["source_paths"] if key.startswith("eval_summary_")]
    ) == 72
    _assert_live_path_hashes(metadata["source_paths"], metadata["source_hashes"])

    recomputed_rows, recomputed, recomputed_blocks = score_heldout(
        protocol_path=PROTOCOL_PATH,
        predictions_path=BLIND_PATH,
        eval_manifests=EVAL_MANIFESTS,
        out_rows_path=tmp_path / "rows.csv",
        out_summary_path=tmp_path / "summary.json",
        out_blocks_path=tmp_path / "blocks.csv",
        created_utc="2026-07-10T00:00:00+00:00",
    )
    assert len(recomputed_rows) == len(scored_rows) == 72
    assert recomputed["raw_confusion"] == stored["raw_confusion"]
    assert recomputed["blocks"] == stored["blocks"] == recomputed_blocks
    assert recomputed["metadata"]["source_hashes"] == metadata["source_hashes"]
    assert set(recomputed["metadata"]["source_paths"]) == set(
        metadata["source_paths"]
    )
    for key, expected in stored["metrics"].items():
        actual = recomputed["metrics"][key]
        if isinstance(expected, float):
            assert actual == pytest.approx(expected)
        else:
            assert actual == expected

    truth = [_csv_bool(row["behavior_label"]) for row in scored_rows]
    predicted = [_csv_bool(row["frozen_gate_pass"]) for row in scored_rows]
    confusion = {
        "tp": sum(t and p for t, p in zip(truth, predicted)),
        "tn": sum(not t and not p for t, p in zip(truth, predicted)),
        "fp": sum(not t and p for t, p in zip(truth, predicted)),
        "fn": sum(t and not p for t, p in zip(truth, predicted)),
    }
    assert stored["raw_confusion"] == confusion
    assert sum(confusion.values()) == 72
    metrics = stored["metrics"]
    assert metrics["num_rows"] == 72
    assert metrics["actual_positive"] == confusion["tp"] + confusion["fn"]
    assert metrics["predicted_positive"] == confusion["tp"] + confusion["fp"]
    assert metrics["false_early"] == sum(block["false_early"] for block in stored["blocks"])
    assert metrics["false_late"] == sum(block["false_late"] for block in stored["blocks"])
    for key in ("tp", "tn", "fp", "fn"):
        assert sum(block[key] for block in stored["blocks"]) == confusion[key]


def test_tie_aware_average_precision_is_order_invariant() -> None:
    _, rows = _read_csv(SCORED_ROWS_PATH)
    truth = [_csv_bool(row["behavior_label"]) for row in rows]
    scores = [float(row["joint_score"]) for row in rows]

    expected = 0.9654813594276511
    assert _auprc(truth, scores) == pytest.approx(expected)
    assert _auprc(list(reversed(truth)), list(reversed(scores))) == pytest.approx(
        expected
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("joint_score", "999", "joint_score"),
        ("atr_threshold_margin", "999", "atr_threshold_margin"),
        ("frozen_gate_pass", "__flip__", "gate decision"),
    ),
)
def test_score_rejects_tampered_blind_gate_fields(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    fields, rows = _read_csv(BLIND_PATH)
    if value == "__flip__":
        rows[0][field] = "false" if rows[0][field] == "true" else "true"
    else:
        rows[0][field] = value
    predictions = tmp_path / "blind.csv"
    with predictions.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    sidecar = _strict_json(BLIND_SIDECAR_PATH)
    sidecar["metadata"]["source_paths"]["blind_rows"] = str(predictions)
    sidecar["metadata"]["source_hashes"]["blind_rows"] = _sha256(predictions)
    sidecar_path = Path(f"{predictions}.metadata.json")
    sidecar_path.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=message):
        score_heldout(
            protocol_path=PROTOCOL_PATH,
            predictions_path=predictions,
            eval_manifests=EVAL_MANIFESTS,
            out_rows_path=tmp_path / "rows.csv",
            out_summary_path=tmp_path / "summary.json",
            out_blocks_path=tmp_path / "blocks.csv",
        )


def test_external_builder_parsers_expose_no_threshold_or_tau_controls() -> None:
    parsers = (
        build_external_atr_parser(),
        build_external_smpr_parser(),
        build_diagnostic_parser(),
    )
    for parser in parsers:
        names = {
            name.lower().replace("-", "_")
            for action in parser._actions
            for name in (action.dest, *action.option_strings)
        }
        assert not any("threshold" in name or "tau" in name for name in names)

    diagnostic_destinations = {action.dest for action in parsers[-1]._actions}
    diagnostic_parameters = set(inspect.signature(build_diagnostic_input).parameters)
    assert "eval_manifest" not in diagnostic_destinations
    assert "eval_manifests" not in diagnostic_destinations
    assert "eval_manifest" not in diagnostic_parameters
    assert "eval_manifests" not in diagnostic_parameters
