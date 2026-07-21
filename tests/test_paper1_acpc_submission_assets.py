from __future__ import annotations

import csv
import json
from pathlib import Path

from paper1.scripts.build_acpc_submission_assets import (
    build_absolute_table,
    build_increment_table,
    build_pldm_table,
    build_sweep_table,
)


ROOT = Path(__file__).resolve().parents[1]


def _planner_summary() -> dict:
    path = ROOT / "paper1/results/acpc_planner_stability_v4/summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_submission_planner_tables_are_bound_to_validated_three_seed_summary() -> None:
    summary = _planner_summary()

    assert summary["validated_shard_count"] == 72
    assert summary["training_seeds"] == [3072, 3073, 3074]
    assert summary["invariants"]["pass"] is True

    increment = build_increment_table(summary)
    assert r"7.9 $\pm$ 1.4 & 8/12" in increment
    assert r"15.2 $\pm$ 2.0 & 12/12" in increment
    assert r"1.1 $\pm$ 0.5 & 10/12" in increment
    assert "standard deviation across three runs" in increment
    assert "Reduction in prediction MAE" in increment
    assert "fitted on three tasks and evaluated on the remaining task" in increment
    assert "Held-out" not in increment
    assert "Task--run evaluations" in increment
    assert "Run range" not in increment
    assert "seed 3072" not in increment
    assert "Three-seed" not in increment

    absolute = build_absolute_table(summary)
    assert "TwoRoom & 0.13$\\pm$0.03 & 0.93$\\pm$0.02" in absolute
    assert (
        "Equal-task mean & 0.09$\\pm$0.03 & 0.93$\\pm$0.01 & "
        "227.04$\\pm$16.92 & 3.64$\\pm$0.68"
    ) in absolute
    assert "not an environment success rate" in absolute


def test_pldm_table_uses_the_current_task_relative_protocol() -> None:
    rows_path = ROOT / "paper1/results/external_validation/pldm_frozen_rows_v2.csv"
    with rows_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    cross_task = json.loads(
        (
            ROOT / "paper1/results/cross_task_ir_dr_all_subsets_summary_v1.json"
        ).read_text(encoding="utf-8")
    )

    table = build_pldm_table(rows, cross_task)
    assert "leave-task-out IR--DR screen in two model families" in table
    assert "TwoRoom & 0.935 & 0.938" in table
    assert "PushT & 0.917 & 0.750" in table
    assert "Reacher & 0.889 & 0.500" in table
    assert "Cube & 0.858 & 0.875" in table
    assert "within-task IR normalization yields identical PLDM decisions" in table


def test_submission_full_sweep_table_keeps_all_tasks_and_nine_levels() -> None:
    path = ROOT / "paper1/results/full_sweep_diagnostics_summary.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == 36
    assert {row["task"] for row in rows} == {
        "TwoRoom",
        "PushT",
        "Reacher",
        "Cube",
    }
    table = build_sweep_table(rows)
    assert "nine checkpoints per task" in table
    assert "TwoRoom & 68.8 & 97.1" in table
    assert "PushT & 7.2 & 86.8" in table
    assert "Reacher & 18.2 & 83.3" in table
    assert "Cube & 43.1 & 66.0" in table
    assert "Relative IR & DR" in table
