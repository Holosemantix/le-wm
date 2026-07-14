from __future__ import annotations

import csv
import json
from pathlib import Path

from paper1.scripts.build_acpc_submission_assets import (
    build_absolute_table,
    build_increment_table,
    build_sweep_table,
)


ROOT = Path(__file__).resolve().parents[1]


def _planner_summary() -> dict:
    path = ROOT / "paper1/results/acpc_planner_stability_v2/summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_submission_planner_tables_are_bound_to_validated_v2_summary() -> None:
    summary = _planner_summary()

    assert summary["validated_shard_count"] == 24
    assert summary["invariants"]["pass"] is True

    increment = build_increment_table(summary)
    assert r"\textbf{9.5\%}" in increment
    assert r"\textbf{12.9\%}" in increment
    assert "0.8\\%" in increment
    assert "3/4" in increment
    assert "4/4" in increment

    absolute = build_absolute_table(summary)
    assert "TwoRoom & 0.16 & 0.91 & 192.38 & 5.31" in absolute
    assert "Equal-task mean & 0.12 & 0.93 & 208.86 & 2.85 & 218.69 & 1.01" in absolute
    assert "not closed-loop return" in absolute


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
    assert "complete nine-level Gaussian training sweep" in table
    assert "TwoRoom & 68.8 & 97.1" in table
    assert "PushT & 7.2 & 86.8" in table
    assert "Reacher & 18.2 & 83.3" in table
    assert "Cube & 43.1 & 66.0" in table
