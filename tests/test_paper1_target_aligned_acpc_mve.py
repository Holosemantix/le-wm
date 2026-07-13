from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest
import torch

from paper1.scripts.run_target_aligned_acpc_feasibility import (
    _canonical_task,
    _eval_matched_goal_index,
    _task_state_key,
)
from paper1.scripts.run_target_aligned_acpc_mve import (
    _grouped_ridge_predictions,
    _load_replay_cache,
    _per_group_spearman,
    _rank_rows,
    _replay_cache_key,
    _write_replay_cache,
)


def test_eval_matched_goal_is_current_plus_planning_horizon() -> None:
    assert _eval_matched_goal_index(
        current_index=2,
        plan_horizon=5,
        action_block=5,
        frameskip=5,
        num_steps=12,
    ) == 7

    with pytest.raises(ValueError):
        _eval_matched_goal_index(
            current_index=2,
            plan_horizon=5,
            action_block=5,
            frameskip=4,
            num_steps=12,
        )


@pytest.mark.parametrize(
    ("raw", "expected", "state_key"),
    [
        ("tworoom", "TwoRoom", "proprio"),
        ("pusht", "PushT", "state"),
        ("reacher", "Reacher", "qpos+qvel"),
        ("ogbench/cube_single_expert", "Cube", "qpos+qvel"),
    ],
)
def test_four_tasks_share_one_canonical_runner_contract(
    raw: str,
    expected: str,
    state_key: str,
) -> None:
    assert _canonical_task(None, raw) == expected
    assert _task_state_key(expected) == state_key


def test_rank_rows_uses_stable_low_cost_order() -> None:
    values = torch.tensor(
        [
            [3.0, 1.0, 2.0],
            [0.0, 0.0, 1.0],
        ]
    )

    ranks = _rank_rows(values)

    assert ranks.tolist() == [[2, 0, 1], [0, 1, 2]]


def test_within_history_encoder_constant_is_not_counted_as_evidence() -> None:
    rows = []
    for block in range(3):
        for candidate in range(5):
            rows.append(
                {
                    "trajectory_block_index": block,
                    "severity": 0.05,
                    "draw_index": 0,
                    "encoder": float(block + 1),
                    "target": float(candidate),
                }
            )

    result = _per_group_spearman(
        rows,
        signal="encoder",
        target="target",
    )

    assert result["finite_group_count"] == 0
    assert result["total_group_count"] == 3
    assert result["mean"] is None


def test_grouped_ridge_holds_out_entire_trajectory_blocks() -> None:
    rows = []
    for block in range(5):
        for candidate in range(6):
            feature = float(candidate - 2 * block)
            rows.append(
                {
                    "trajectory_block_index": block,
                    "severity": 0.05,
                    "feature": feature,
                    "target": 3.0 * feature + 0.25,
                }
            )

    result = _grouped_ridge_predictions(
        rows,
        feature_names=("feature",),
        target_name="target",
    )

    assert result["status"] == "complete"
    assert result["group_count"] == 5
    assert result["row_count"] == 30
    assert result["spearman"] > 0.99
    assert result["mean_within_group_spearman"] == pytest.approx(1.0)
    assert len(result["per_group"]) == 5
    assert {
        item["trajectory_block_index"] for item in result["per_group"]
    } == set(range(5))


def test_replay_cache_is_bound_to_exact_state_and_candidate_support(
    tmp_path,
) -> None:
    blocks = [SimpleNamespace(episode_id=3, start_step=7)]
    current = np.arange(4, dtype=np.float64).reshape(1, 4)
    goals = np.arange(2, dtype=np.float64).reshape(1, 2)
    actions = np.arange(20, dtype=np.float32).reshape(1, 1, 10, 2)
    key = _replay_cache_key(
        task="Reacher",
        blocks=blocks,
        current_states=current,
        goal_states=goals,
        candidate_raw_actions=actions,
        action_block=5,
        replay_seed=0,
    )
    replay = {
        "block_states": np.ones((1, 1, 2, 4)),
        "endpoints": np.ones((1, 1, 4)),
        "goal_distances": np.ones((1, 1)),
        "block_pixels": np.ones((1, 1, 2, 3, 3, 3), dtype=np.uint8),
    }
    path = tmp_path / "replay.npz"

    _write_replay_cache(path, cache_key=key, replay=replay)
    loaded = _load_replay_cache(path, expected_key=key)

    assert all(
        np.array_equal(loaded[name], value)
        for name, value in replay.items()
    )
    changed_actions = actions.copy()
    changed_actions[0, 0, 0, 0] += 1.0
    changed_key = _replay_cache_key(
        task="Reacher",
        blocks=blocks,
        current_states=current,
        goal_states=goals,
        candidate_raw_actions=changed_actions,
        action_block=5,
        replay_seed=0,
    )
    assert changed_key != key
    with pytest.raises(RuntimeError, match="key mismatch"):
        _load_replay_cache(path, expected_key=changed_key)
