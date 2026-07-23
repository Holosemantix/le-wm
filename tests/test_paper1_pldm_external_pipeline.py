from __future__ import annotations

import csv
import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from paper1.scripts.build_external_pldm_acpc_horizon_v2_artifact import (
    build_parser as build_atr_parser,
)
from paper1.scripts.build_external_pldm_smpr_v2_artifact import (
    build_parser as build_smpr_parser,
)
from paper1.scripts.build_frozen_diagnostic_input import ROW_FIELDS
from paper1.scripts.build_pldm_canonical_manifest_v2 import (
    build_parser as build_manifest_parser,
)
from paper1.scripts.build_pldm_frozen_diagnostic_input import (
    build_diagnostic_input,
    build_parser as build_diagnostic_parser,
)
from paper1.scripts.frozen_external_validation import BLIND_FIELDS


PROTOCOL_PATH = ROOT / "paper1/config/frozen_diagnostic_protocol_v1.json"
MANIFEST_PATH = ROOT / "assets/paper1_data/canonical_evals_pldm_v2.json"
EXTERNAL_ROOT = ROOT / "paper1/results/remediation_phase2_external_sources/pldm_canonical"
ATR_PATH = EXTERNAL_ROOT / "acpc_horizon_v2_checkpoint_bound.json"
SMPR_PATH = EXTERNAL_ROOT / "smpr_v2_checkpoint_bound.json"
DIAGNOSTIC_PATH = (
    ROOT / "paper1/results/external_validation/pldm_canonical_diagnostic_input_v3.json"
)
BLIND_PATH = (
    ROOT / "paper1/results/external_validation/pldm_frozen_predictions_blind_v2.csv"
)
BLIND_SIDECAR_PATH = Path(f"{BLIND_PATH}.metadata.json")
MULTISEED_ROOT = ROOT / "paper1/results/pldm_multiseed_v2"
MULTISEED_MANIFEST_ROOT = (
    ROOT / "assets/paper1_data/training_seed_eval_manifests"
)
TASKS = ("TwoRoom", "PushT", "Reacher", "Cube")
RHO_GRID = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08)
EXPECTED_GRID = {(task, rho) for task in TASKS for rho in RHO_GRID}
FORBIDDEN_BEHAVIOR_FIELDS = (
    "behavior",
    "success",
    "score",
    "label",
    "return",
    "recovery",
    "ground_truth",
    "reward",
)


def _strict_json(path: Path) -> dict[str, Any]:
    payload = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )
    assert isinstance(payload, dict)
    return payload


@lru_cache(maxsize=None)
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


def _assert_behavior_free(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        for field in row:
            lowered = field.lower()
            assert not any(part in lowered for part in FORBIDDEN_BEHAVIOR_FIELDS), field


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        return list(reader.fieldnames or ()), rows


def test_manifest_seed_comes_from_36_configs_and_checkpoint_hashes_are_live() -> None:
    manifest = _strict_json(MANIFEST_PATH)
    metadata = manifest["_metadata"]
    rows = metadata["checkpoint_rows"]
    source_paths = metadata["source_paths"]
    source_hashes = metadata["source_hashes"]
    config_keys = {key for key in source_paths if key.startswith("config_")}
    checkpoint_keys = {
        key for key in source_paths if key.startswith("checkpoint_")
    }

    assert metadata["schema_version"] == "paper1-pldm-canonical-eval-manifest-0.2"
    assert metadata["status"] == "complete"
    assert metadata["status_counts"] == {"ok": 36}
    assert metadata["missing_rows"] == []
    assert metadata["errors"] == []
    assert metadata["model_family"] == "PLDM"
    assert metadata["training_family_id"] == "pldm_canonical_seed3072"
    assert metadata["training_seed"] == 3072
    assert metadata["training_seed_source"] == "all 36 checkpoint-local config.yaml files"
    assert metadata["training_seed_semantics"] == (
        "one independently trained PLDM checkpoint family"
    )
    assert len(rows) == len(config_keys) == len(checkpoint_keys) == 36
    assert {(row["task"], float(row["std_key"])) for row in rows} == EXPECTED_GRID
    assert {row["training_seed"] for row in rows} == {3072}
    _assert_live_path_hashes(source_paths, source_hashes)

    config_seeds = set()
    for row in rows:
        source_key = f"{row['task']}_{row['std_key']}"
        config_path = Path(row["config_path"])
        checkpoint_path = Path(row["model_file"])
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        config_seeds.add(int(config["seed"]))
        assert source_paths[f"config_{source_key}"] == str(config_path)
        assert source_paths[f"checkpoint_{source_key}"] == str(checkpoint_path)
        assert source_hashes[f"config_{source_key}"] == row["config_sha256"]
        assert source_hashes[f"checkpoint_{source_key}"] == row["model_sha256"]
        assert _sha256(config_path) == row["config_sha256"]
        assert _sha256(checkpoint_path) == row["model_sha256"]
    assert config_seeds == {3072}
    assert _sha256(_repo_path(metadata["script_path"])) == metadata["script_sha256"]


def test_checkpoint_bound_atr_and_smpr_match_manifest_and_each_other() -> None:
    manifest = _strict_json(MANIFEST_PATH)
    protocol_sha = _sha256(PROTOCOL_PATH)
    expected_checkpoints = {
        (row["task"], float(row["std_key"])): row
        for row in manifest["_metadata"]["checkpoint_rows"]
    }
    artifacts = (
        (
            _strict_json(ATR_PATH),
            "pldm_canonical_external_atr",
            "paper1-acpc-horizon-v2-1.0",
        ),
        (
            _strict_json(SMPR_PATH),
            "pldm_canonical_external_smpr",
            "paper1-smpr-v2-merged-1.0",
        ),
    )
    indices: list[dict[tuple[str, float], dict[str, Any]]] = []

    for artifact, role, schema in artifacts:
        metadata = artifact["metadata"]
        rows = artifact["rows"]
        index = {
            (row["task"], float(row["training_rho"])): row for row in rows
        }
        indices.append(index)

        assert metadata["schema_version"] == schema
        assert metadata["artifact_role"] == role
        assert metadata["status"] == "complete"
        assert metadata["status_counts"] == {"ok": 36}
        assert metadata["missing_rows"] == []
        assert metadata["errors"] == []
        assert metadata["behavior_blind"] is True
        assert metadata["split_name"] == "E2"
        assert metadata["protocol_sha256"] == protocol_sha
        assert metadata["protocol_hash"] == protocol_sha
        assert metadata["model_family"] == "PLDM"
        assert metadata["training_family_id"] == "pldm_canonical_seed3072"
        assert metadata["training_seed"] == 3072
        assert len(rows) == 36
        assert set(index) == EXPECTED_GRID
        assert {row["status"] for row in rows} == {"ok"}
        assert {row["split_name"] for row in rows} == {"E2"}
        assert {row["model_family"] for row in rows} == {"PLDM"}
        assert {row["training_seed"] for row in rows} == {3072}
        _assert_behavior_free(rows)
        _assert_live_path_hashes(
            metadata["source_paths"], metadata["source_hashes"]
        )
        _assert_live_path_hashes(
            metadata["implementation_paths"], metadata["implementation_hashes"]
        )
        assert (
            _sha256(_repo_path(metadata["script_path"]))
            == metadata["script_sha256"]
        )

    atr_index, smpr_index = indices
    for key, expected in expected_checkpoints.items():
        atr_row = atr_index[key]
        smpr_row = smpr_index[key]
        checkpoint_path = Path(expected["model_file"])
        assert atr_row["model_file"] == smpr_row["model_file"] == str(checkpoint_path)
        assert (
            atr_row["checkpoint_sha256"]
            == smpr_row["checkpoint_sha256"]
            == expected["model_sha256"]
            == _sha256(checkpoint_path)
        )
        assert smpr_row["reference_atr_horizon_v2_q90"] == pytest.approx(
            atr_row["atr_horizon_v2_q90"]
        )
        assert smpr_row["atr_reference_match"] is True


def test_pldm_diagnostic_v2_is_strict_36_row_allowlisted_contract() -> None:
    artifact = _strict_json(DIAGNOSTIC_PATH)
    metadata = artifact["metadata"]
    rows = artifact["rows"]

    assert metadata["schema_version"] == "paper1-frozen-diagnostic-input-1.0"
    assert metadata["strict_external_contract"] == "pldm_canonical_gaussian_e2_v1"
    assert metadata["status"] == "complete"
    assert metadata["status_counts"] == {"ok": 36}
    assert metadata["missing_rows"] == []
    assert metadata["errors"] == []
    assert metadata["behavior_blind"] is True
    assert metadata["threshold_search_available"] is False
    assert metadata["split_name"] == "E2"
    assert metadata["training_family_id"] == "pldm_canonical_seed3072"
    assert metadata["training_seed"] == 3072
    assert metadata["training_seed_semantics"] == (
        "one independently trained PLDM checkpoint family"
    )
    assert metadata["protocol_sha256"] == _sha256(PROTOCOL_PATH)
    assert len(rows) == 36
    assert all(set(row) == set(ROW_FIELDS) for row in rows)
    assert {(row["task"], row["training_rho"]) for row in rows} == EXPECTED_GRID
    assert {row["status"] for row in rows} == {"ok"}
    assert {row["split_name"] for row in rows} == {"E2"}
    assert {row["model_family"] for row in rows} == {"PLDM"}
    assert {row["training_seed"] for row in rows} == {3072}
    _assert_behavior_free(rows)
    _assert_live_path_hashes(metadata["source_paths"], metadata["source_hashes"])
    assert _sha256(_repo_path(metadata["script_path"])) == metadata["script_sha256"]

    rebuilt = build_diagnostic_input(
        protocol_path=PROTOCOL_PATH,
        atr_path=ATR_PATH,
        smpr_path=SMPR_PATH,
    )
    assert rebuilt["rows"] == rows
    assert rebuilt["metadata"]["strict_external_contract"] == (
        metadata["strict_external_contract"]
    )
    assert rebuilt["metadata"]["source_hashes"] == metadata["source_hashes"]


def test_pldm_blind_sidecar_binds_36_rows() -> None:
    sidecar = _strict_json(BLIND_SIDECAR_PATH)
    metadata = sidecar["metadata"]
    fields, rows = _read_csv(BLIND_PATH)
    protocol_sha = _sha256(PROTOCOL_PATH)
    diagnostic_sha = _sha256(DIAGNOSTIC_PATH)

    assert fields == sidecar["fields"] == list(BLIND_FIELDS)
    assert sidecar["row_count"] == len(rows) == 36
    assert metadata["status"] == "complete"
    assert metadata["status_counts"] == {"ok": 36}
    assert metadata["behavior_blind"] is True
    assert metadata["threshold_search_available"] is False
    assert metadata["protocol_hash"] == protocol_sha
    assert metadata["training_seed_semantics"] == (
        "one independently trained PLDM checkpoint family"
    )
    assert metadata["source_hashes"]["blind_rows"] == _sha256(BLIND_PATH)
    assert metadata["source_hashes"]["diagnostics"] == diagnostic_sha
    _assert_live_path_hashes(metadata["source_paths"], metadata["source_hashes"])
    assert {row["model_family"] for row in rows} == {"PLDM"}
    assert {row["training_family_id"] for row in rows} == {
        "pldm_canonical_seed3072"
    }
    assert {row["training_seed"] for row in rows} == {"3072"}
    assert {row["split_name"] for row in rows} == {"E2"}
    assert {row["protocol_sha256"] for row in rows} == {protocol_sha}
    assert {row["diagnostics_sha256"] for row in rows} == {diagnostic_sha}
    assert _sha256(_repo_path(metadata["script_path"])) == metadata["script_sha256"]


def test_pldm_pipeline_parsers_expose_no_gate_recalibration_controls() -> None:
    parsers = (
        build_manifest_parser(),
        build_atr_parser(),
        build_smpr_parser(),
        build_diagnostic_parser(),
    )
    for parser in parsers:
        names = {
            name.lower().replace("-", "_")
            for action in parser._actions
            for name in (action.dest, *action.option_strings)
        }
        assert not any(
            forbidden in name
            for forbidden in ("tau", "threshold", "calibration")
            for name in names
        )


@pytest.mark.parametrize("training_seed", (3073, 3074))
def test_new_pldm_training_families_are_complete_and_protocol_bound(
    training_seed: int,
) -> None:
    protocol_sha = _sha256(PROTOCOL_PATH)
    family_id = f"pldm_canonical_seed{training_seed}"
    manifest = _strict_json(
        MULTISEED_MANIFEST_ROOT / f"pldm_seed{training_seed}_evals.json"
    )
    manifest_metadata = manifest["_metadata"]
    assert manifest_metadata["status"] == "complete"
    assert manifest_metadata["status_counts"] == {"ok": 36}
    assert manifest_metadata["training_family_id"] == family_id
    assert manifest_metadata["training_seed"] == training_seed
    assert len(manifest_metadata["checkpoint_rows"]) == 36

    seed_root = MULTISEED_ROOT / f"seed{training_seed}"
    for filename, schema in (
        ("acpc_horizon_v2_checkpoint_bound.json", "paper1-acpc-horizon-v2-1.0"),
        ("smpr_v2_checkpoint_bound.json", "paper1-smpr-v2-merged-1.0"),
        ("diagnostic_input.json", "paper1-frozen-diagnostic-input-1.0"),
    ):
        artifact = _strict_json(seed_root / filename)
        metadata = artifact["metadata"]
        rows = artifact["rows"]
        assert metadata["schema_version"] == schema
        assert metadata["status"] == "complete"
        assert metadata["status_counts"] == {"ok": 36}
        assert metadata["training_family_id"] == family_id
        assert metadata["training_seed"] == training_seed
        assert metadata["protocol_sha256"] == protocol_sha
        assert len(rows) == 36
        assert {
            (row["task"], float(row["training_rho"])) for row in rows
        } == EXPECTED_GRID
        assert {row["status"] for row in rows} == {"ok"}

    blind_path = seed_root / "frozen_predictions_blind.csv"
    sidecar = _strict_json(Path(f"{blind_path}.metadata.json"))
    fields, rows = _read_csv(blind_path)
    assert fields == sidecar["fields"] == list(BLIND_FIELDS)
    assert sidecar["row_count"] == len(rows) == 36
    assert sidecar["metadata"]["status"] == "complete"
    assert sidecar["metadata"]["protocol_hash"] == protocol_sha
    assert sidecar["metadata"]["source_hashes"]["blind_rows"] == _sha256(
        blind_path
    )
    assert {row["training_family_id"] for row in rows} == {family_id}
    assert {int(row["training_seed"]) for row in rows} == {training_seed}
