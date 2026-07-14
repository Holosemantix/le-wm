from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from paper1.scripts.freeze_acpc_planner_three_seed_protocol import (
    EXTENSION_SEEDS,
    FORMAL_SEEDS,
    TASKS,
    adaptive_arguments,
    checkpoint_path,
    fixed_arguments,
)
from paper1.scripts.summarize_acpc_planner_three_seed import (
    _join_reduced,
    _three_seed_incremental_analyses,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "paper1/config/acpc_planner_stability_protocol_v3.json"
EXECUTION = ROOT / "paper1/config/acpc_planner_stability_execution_v3.json"
REFERENCE_EXECUTION = (
    ROOT / "paper1/config/acpc_planner_stability_execution_v2.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _synthetic_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for seed_index, seed in enumerate(FORMAL_SEEDS):
        for task_index, task in enumerate(("Cube", "PushT", "Reacher", "TwoRoom")):
            for role_index, role in enumerate(("base", "endpoint")):
                for severity in (0.02, 0.05, 0.08):
                    for block in range(8):
                        h1 = 0.2 + 0.01 * block + 0.03 * task_index
                        h5 = (
                            severity * (1.0 + 0.1 * block)
                            + 0.02 * role_index
                            + 0.005 * seed_index
                        )
                        rows.append(
                            {
                                "training_seed": seed,
                                "task": task,
                                "checkpoint_role": role,
                                "severity": severity,
                                "h1": h1,
                                "h5": h5,
                                "margin": 0.5 + 0.02 * block,
                                "cost_drift": 3.0 * h5,
                                "first_action_rms": 2.0 * h5,
                                "positive_clean_regret": h5,
                            }
                        )
    return rows


def test_extension_checkpoint_and_argument_grid_is_complete() -> None:
    for task_name, task in TASKS.items():
        for seed in EXTENSION_SEEDS:
            for role in ("base", "endpoint"):
                assert checkpoint_path(task, seed, role).is_file()
                fixed = fixed_arguments(task_name, task, seed, role)
                reduced = adaptive_arguments(
                    task_name, task, seed, role, full_budget=False
                )
                full = adaptive_arguments(
                    task_name, task, seed, role, full_budget=True
                )
                assert fixed["training_seed"] == seed
                assert fixed["severities"] == [0.0, 0.02, 0.05, 0.08]
                assert fixed["candidate_count"] == 64
                assert reduced["n_blocks"] == 100
                assert reduced["n_steps"] == 8
                assert full["n_blocks"] == 16
                assert full["candidate_count"] == 300
                assert full["n_steps"] == 30


def test_reduced_join_key_includes_training_seed() -> None:
    loaded = []
    for seed in FORMAL_SEEDS:
        base = {
            "training_seed": seed,
            "task": "TwoRoom",
            "checkpoint_role": "base",
            "trajectory_block_id": "episode-1",
            "severity": 0.08,
            "draw_index": 0,
        }
        loaded.extend(
            [
                {
                    "shard": {"analysis_role": "fixed_reduced"},
                    "payload": {"rows": [dict(base)]},
                },
                {
                    "shard": {"analysis_role": "adaptive_reduced"},
                    "payload": {"rows": [dict(base)]},
                },
            ]
        )
    joined = _join_reduced(loaded)
    assert len(joined) == 3
    assert {row["fixed"]["training_seed"] for row in joined} == set(FORMAL_SEEDS)


@pytest.mark.parametrize(
    "response", ["cost_drift", "first_action_rms", "positive_clean_regret"]
)
def test_three_seed_analysis_fits_each_seed_independently(response: str) -> None:
    analysis = _three_seed_incremental_analyses(_synthetic_rows())[response]
    assert set(analysis["per_seed"]) == {"3072", "3073", "3074"}
    assert analysis["three_seed_summary"]["positive_seed_count"] == 3
    assert analysis["three_seed_summary"]["task_seed_cells_improved"] == 12
    assert analysis["three_seed_summary"]["directionally_consistent"] is True
    assert analysis["lobo_ridge"]["task_count"] == 12


def test_frozen_v3_manifest_binds_reference_and_exact_extension() -> None:
    if not PROTOCOL.is_file() or not EXECUTION.is_file():
        pytest.skip("v3 protocol has not been frozen yet")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    reference = json.loads(REFERENCE_EXECUTION.read_text(encoding="utf-8"))

    assert protocol["status"] == "frozen_pre_execution"
    assert protocol["immutable"] is True
    assert protocol["frozen_panel"]["formal_training_seeds"] == list(FORMAL_SEEDS)
    assert execution["parent_protocol"]["sha256"] == _sha256(PROTOCOL)
    assert execution["result_root"] == (
        "paper1/results/acpc_planner_stability_v3/formal"
    )
    shards = execution["authorized_shards"]
    assert len(shards) == 48
    assert Counter(
        (row["analysis_role"], row["arguments"]["training_seed"])
        for row in shards
    ) == Counter(
        (role, seed)
        for seed in EXTENSION_SEEDS
        for role in ("fixed_reduced", "adaptive_reduced", "adaptive_full")
        for _ in range(8)
    )

    reference_by_cell = {
        (
            row["analysis_role"],
            row["arguments"]["task"],
            row["arguments"]["checkpoint_role"],
        ): row
        for row in reference["authorized_shards"]
    }
    allowed_differences = {"training_seed", "anonymous_checkpoint_id"}
    for shard in shards:
        key = (
            shard["analysis_role"],
            shard["arguments"]["task"],
            shard["arguments"]["checkpoint_role"],
        )
        reference_arguments = reference_by_cell[key]["arguments"]
        actual = {
            key: value
            for key, value in shard["arguments"].items()
            if key not in allowed_differences
        }
        expected = {
            key: value
            for key, value in reference_arguments.items()
            if key not in allowed_differences
        }
        assert actual == expected

    for path, expected in protocol["source_hashes"].items():
        assert _sha256(ROOT / path) == expected
    for frozen in (PROTOCOL, EXECUTION):
        digest, name = frozen.with_suffix(frozen.suffix + ".sha256").read_text(
            encoding="utf-8"
        ).split()
        assert name == frozen.name
        assert digest == _sha256(frozen)
