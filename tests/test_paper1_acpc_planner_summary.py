from __future__ import annotations

import pytest

from paper1.scripts.summarize_acpc_planner_stability import (
    _feature_matrix,
    _lobo_ridge,
)


def _synthetic_rows() -> list[dict[str, float | str]]:
    rows = []
    tasks = ["Cube", "PushT", "Reacher", "TwoRoom"]
    for task_index, task in enumerate(tasks):
        for role_index, role in enumerate(("base", "endpoint")):
            for severity in (0.02, 0.05, 0.08):
                for block in range(8):
                    h1 = 0.2 + 0.01 * block + 0.03 * task_index
                    h5 = severity * (1.0 + 0.1 * block) + 0.02 * role_index
                    rows.append(
                        {
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


def test_feature_contract_adds_only_h5_column() -> None:
    rows = _synthetic_rows()[:4]
    baseline = _feature_matrix(rows, include_h5=False)
    full = _feature_matrix(rows, include_h5=True)

    assert baseline.shape == (4, 4)
    assert full.shape == (4, 5)
    assert (full[:, :4] == baseline).all()


@pytest.mark.parametrize(
    "response", ["cost_drift", "first_action_rms", "positive_clean_regret"]
)
def test_lobo_h5_recovers_planner_linked_synthetic_signal(response: str) -> None:
    result = _lobo_ridge(_synthetic_rows(), response=response)

    assert result["task_count"] == 4
    assert result["tasks_improved"] == 4
    assert result["equal_task_plus_h5_log1p_mae"] < result[
        "equal_task_baseline_log1p_mae"
    ]
