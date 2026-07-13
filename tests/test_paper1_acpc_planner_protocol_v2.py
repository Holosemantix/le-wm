from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "paper1/config/acpc_planner_stability_protocol_v2.json"
EXECUTION = ROOT / "paper1/config/acpc_planner_stability_execution_v2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_sidecar(path: Path) -> None:
    sidecar = path.with_suffix(path.suffix + ".sha256")
    digest, filename = sidecar.read_text(encoding="utf-8").strip().split()
    assert filename == path.name
    assert digest == _sha256(path)


def test_v2_protocol_binds_numerical_correction_and_v1_attempts() -> None:
    protocol = _load(PROTOCOL)
    assert protocol["status"] == "frozen_pre_execution"
    assert protocol["immutable"] is True
    correction = protocol["correction_history"]
    assert correction["v1_results_must_be_retained"] is True
    attempts = correction["v1_attempts"]
    assert len(attempts) == 24
    fixed = [row for row in attempts if row["analysis_role"] == "fixed_reduced"]
    adaptive = [row for row in attempts if row["analysis_role"] != "fixed_reduced"]
    assert len(fixed) == 8
    assert len(adaptive) == 16
    assert all(row["status"] == "partial" and row["actual_rows"] == 100 for row in fixed)
    assert all(row["status"] == "complete" for row in adaptive)
    for path, expected in protocol["source_hashes"].items():
        assert _sha256(ROOT / path) == expected
    _assert_sidecar(PROTOCOL)


def test_v2_execution_reruns_all_shards_with_only_fixed_runner_changed() -> None:
    protocol = _load(PROTOCOL)
    execution = _load(EXECUTION)
    assert execution["parent_protocol"]["sha256"] == _sha256(PROTOCOL)
    assert execution["result_root"] == "paper1/results/acpc_planner_stability_v2/formal"
    shards = execution["authorized_shards"]
    assert len(shards) == 24
    fixed = [row for row in shards if row["analysis_role"] == "fixed_reduced"]
    adaptive = [row for row in shards if row["analysis_role"] != "fixed_reduced"]
    assert len(fixed) == 8
    assert len(adaptive) == 16
    assert {row["runner"] for row in fixed} == {
        "tools/paper1_acpc_planner_stability_audit_v2.py"
    }
    assert {row["runner"] for row in adaptive} == {
        "tools/paper1_acpc_adaptive_cem_audit.py"
    }
    assert all(
        row["output_path"].startswith(execution["result_root"] + "/")
        for row in shards
    )
    assert protocol["claim_adjudication"]
    _assert_sidecar(EXECUTION)
