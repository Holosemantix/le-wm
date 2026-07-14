from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
V3_PROTOCOL = ROOT / "paper1/config/acpc_planner_stability_protocol_v3.json"
V3_EXECUTION = ROOT / "paper1/config/acpc_planner_stability_execution_v3.json"
V3_RESULTS = ROOT / "paper1/results/acpc_planner_stability_v3/formal"
V4_PROTOCOL = ROOT / "paper1/config/acpc_planner_stability_protocol_v4.json"
V4_EXECUTION = ROOT / "paper1/config/acpc_planner_stability_execution_v4.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v4_source_complete_correction_precedes_execution() -> None:
    if not V4_PROTOCOL.is_file() or not V4_EXECUTION.is_file():
        pytest.skip("v4 protocol has not been frozen yet")
    protocol = _load(V4_PROTOCOL)
    execution = _load(V4_EXECUTION)
    correction = protocol["pre_execution_correction"]

    assert protocol["status"] == "frozen_pre_execution"
    assert protocol["immutable"] is True
    assert protocol["protocol_id"] == "paper1-acpc-planner-stability-v4"
    assert correction["results_observed_before_correction"] is False
    assert correction["v3_result_root_absent_at_v4_freeze"] is True
    assert correction["supersedes_unexecuted_protocol"]["sha256"] == _sha256(
        V3_PROTOCOL
    )
    assert correction["supersedes_unexecuted_execution"]["sha256"] == _sha256(
        V3_EXECUTION
    )
    assert not V3_RESULTS.exists()

    assert "paper1/scripts/summarize_acpc_planner_stability.py" in protocol[
        "source_hashes"
    ]
    assert "paper1/scripts/summarize_acpc_planner_three_seed.py" in protocol[
        "source_hashes"
    ]
    for path, expected in protocol["source_hashes"].items():
        assert _sha256(ROOT / path) == expected

    assert execution["parent_protocol"]["sha256"] == _sha256(V4_PROTOCOL)
    assert execution["result_root"] == (
        "paper1/results/acpc_planner_stability_v4/formal"
    )
    assert len(execution["authorized_shards"]) == 48
    assert Counter(
        (
            shard["arguments"]["training_seed"],
            shard["analysis_role"],
        )
        for shard in execution["authorized_shards"]
    ) == Counter(
        (seed, role)
        for seed in (3072, 3073)
        for role in ("fixed_reduced", "adaptive_reduced", "adaptive_full")
        for _ in range(8)
    )

    for frozen in (V4_PROTOCOL, V4_EXECUTION):
        digest, name = frozen.with_suffix(frozen.suffix + ".sha256").read_text(
            encoding="utf-8"
        ).split()
        assert name == frozen.name
        assert digest == _sha256(frozen)
