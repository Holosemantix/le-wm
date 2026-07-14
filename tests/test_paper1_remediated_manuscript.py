from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_future_drift_summary_uses_three_symmetric_training_runs() -> None:
    summary = json.loads(
        (ROOT / "paper1/results/future_drift_three_seed_summary_v1.json").read_text()
    )
    with (ROOT / "paper1/results/future_drift_three_seed_v1.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))

    assert summary["training_seeds"] == [3072, 3073, 3074]
    assert summary["all_seed_task_cells_pass"] is True
    assert len(rows) == 12
    assert {int(row["training_seed"]) for row in rows} == {3072, 3073, 3074}
    assert all(row["pass"] == "True" for row in rows)
    assert math.isclose(summary["mean_reduction_vs_one_step"], 0.5589057064173736)
    assert math.isclose(
        summary["mean_reduction_vs_same_horizon_control"], 0.5129276774853404
    )
    assert math.isclose(summary["sample_sd_reduction_vs_one_step"], 0.047338259788311327)
    assert math.isclose(
        summary["sample_sd_reduction_vs_same_horizon_control"],
        0.03524693071442968,
    )


def test_main_text_uses_reader_facing_data_flow_language() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    lowered = text.lower()

    for excluded in (
        "seed3075",
        "seed 3075",
        "held-out",
        "dev-era",
        "prospective seed",
        "correct-action",
        "table_cross_stressor_robustness_audit",
        "table_seed_transfer_audit",
    ):
        assert excluded not in lowered

    assert "same eight-step latent" in lowered
    assert "all 14 directional" in lowered
    assert "selected from one, two, and three source tasks" in lowered
    assert "action-conditioned predictive consistency" in lowered
    assert "selective consistency" in lowered
    assert "checkpoint-level scores" in lowered


def test_referenced_cross_stressor_outputs_contain_only_final_rule() -> None:
    summary_table = (
        ROOT / "paper1/tables/table_cross_stressor_selective_transfer_v1.tex"
    ).read_text()
    all_pairs_table = (
        ROOT / "paper1/tables/table_cross_stressor_all_pairs_v1.tex"
    ).read_text()
    combined = summary_table + all_pairs_table
    for excluded in (
        "Encoder q90",
        "H1 q90",
        "Correct-action",
        "Action-shuffled",
        "Time-shuffled",
    ):
        assert excluded not in combined
    assert "All pairs & 24 & 0.889" in summary_table
