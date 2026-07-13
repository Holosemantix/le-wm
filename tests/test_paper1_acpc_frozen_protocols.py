from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANNER_PROTOCOL = ROOT / "paper1/config/acpc_planner_stability_protocol_v1.json"
PLANNER_EXECUTION = ROOT / "paper1/config/acpc_planner_stability_execution_v1.json"
P1_PROTOCOL = ROOT / "paper1/config/p1_prospective_seed3075_protocol_v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_sidecar(path: Path) -> None:
    digest, relative = path.with_suffix(path.suffix + ".sha256").read_text().split()
    assert relative == str(path.relative_to(ROOT))
    assert digest == _sha256(path)


def test_planner_protocol_and_execution_are_hash_bound() -> None:
    protocol = _load(PLANNER_PROTOCOL)
    execution = _load(PLANNER_EXECUTION)

    _assert_sidecar(PLANNER_PROTOCOL)
    _assert_sidecar(PLANNER_EXECUTION)
    assert protocol["status"] == "frozen_pre_execution"
    assert protocol["immutable"] is True
    assert execution["parent_protocol"]["sha256"] == _sha256(PLANNER_PROTOCOL)
    for relative, digest in protocol["source_hashes"].items():
        assert _sha256(ROOT / relative) == digest
    assert execution["source_hashes"] == protocol["source_hashes"]


def test_planner_manifest_covers_reduced_and_full_four_task_panel() -> None:
    execution = _load(PLANNER_EXECUTION)
    shards = execution["authorized_shards"]
    roles = Counter(shard["analysis_role"] for shard in shards)

    assert len(shards) == 24
    assert roles == {
        "fixed_reduced": 8,
        "adaptive_reduced": 8,
        "adaptive_full": 8,
    }
    assert len({shard["shard_id"] for shard in shards}) == len(shards)
    assert len({shard["output_path"] for shard in shards}) == len(shards)
    for shard in shards:
        arguments = shard["arguments"]
        assert arguments["training_seed"] == 3074
        assert arguments["trajectory_seed"] == 9101
        assert arguments["probe_seed"] == 20260713
        if shard["analysis_role"] == "adaptive_full":
            assert arguments["candidate_count"] == 300
            assert arguments["n_steps"] == 30


def test_prospective_seed3075_protocol_is_complete_and_hash_bound() -> None:
    protocol = _load(P1_PROTOCOL)

    _assert_sidecar(P1_PROTOCOL)
    assert protocol["status"] == "frozen_pre_execution"
    assert protocol["prospective_boundary"]["training_seed"] == 3075
    assert protocol["prospective_boundary"]["seed3075_output_absent_at_freeze"]
    assert len(protocol["tasks"]) == 4
    for relative, digest in protocol["source_hashes"].items():
        assert _sha256(ROOT / relative) == digest


def test_seed3075_commands_change_seed_not_training_objective() -> None:
    protocol = _load(P1_PROTOCOL)

    for task in protocol["tasks"]:
        command = task["training_command"]
        joined = " ".join(command)
        assert "seed=3075" in command
        assert "image_noise.std_min=0.0" in command
        assert "image_noise.std_max=0.0" in command
        assert "image_noise.noise_prob=0.0" in command
        assert "trainer.max_epochs=10" in command
        assert "swanlab.enabled=false" in command
        assert "wandb.enabled=false" in command
        assert "noise_0to" not in joined
        evaluation = task["evaluation_command"]
        assert evaluation[evaluation.index("--training-seed") + 1] == "3075"
        assert evaluation[evaluation.index("--checkpoint-role") + 1] == "base"
        assert evaluation[evaluation.index("--n-blocks") + 1] == "16"
        assert evaluation[evaluation.index("--draws") + 1] == "2"
