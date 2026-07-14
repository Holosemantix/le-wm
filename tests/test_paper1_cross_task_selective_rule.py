from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from paper1.scripts.build_cross_stressor_selective_transfer import build as build_p3
from paper1.scripts.cross_task_selective_rule import run_all_subsets
from paper1.scripts.utils_paper1_io import read_csv


ROOT = Path(__file__).resolve().parents[1]


def test_all_source_task_subsets_are_complete_and_directional() -> None:
    details, params, summary = run_all_subsets(
        read_csv(ROOT / "paper1/results/full_sweep_diagnostics.csv")
    )

    assert len(details) == 84
    assert len(params["splits"]) == 14
    assert summary["partition_count"] == 14
    assert summary["evaluation_task_incidence_count"] == 28
    assert params["evaluation_outcomes_used_for_selection"] is False

    by_coverage = {item["source_coverage"]: item for item in summary["coverage"]}
    assert [by_coverage[k]["partition_count"] for k in (1, 2, 3)] == [4, 6, 4]
    assert [by_coverage[k]["evaluation_task_incidence_count"] for k in (1, 2, 3)] == [12, 12, 4]
    assert by_coverage[1]["balanced_accuracy"] == pytest.approx(0.8397156085)
    assert by_coverage[2]["balanced_accuracy"] == pytest.approx(0.8552248677)
    assert by_coverage[3]["balanced_accuracy"] == pytest.approx(0.8540674603)

    for split in params["splits"]:
        assert set(split["source_tasks"]).isdisjoint(split["evaluation_tasks"])
        assert set(split["source_tasks"]) | set(split["evaluation_tasks"]) == {
            "TwoRoom",
            "PushT",
            "Reacher",
            "Cube",
        }
        coverage = split["source_coverage"]
        assert split["source_rows"] == coverage * 27
        assert split["evaluation_rows"] == (4 - coverage) * 27


def test_three_source_thresholds_drive_cross_stressor_final_rule() -> None:
    with (ROOT / "paper1/results/external_validation/cross_stressor_all_pairs.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        pairs = list(csv.DictReader(stream))
    p2 = json.loads(
        (ROOT / "paper1/results/cross_task_atr_smpr_all_subsets_summary_v1.json").read_text(
            encoding="utf-8"
        )
    )

    rows, summary = build_p3(pairs, p2)

    assert len(rows) == 24
    assert summary["threshold_search_on_blur_or_resize"] is False
    assert summary["task_thresholds"]["TwoRoom"] == {
        "tau_atr": 0.2,
        "tau_smpr": 0.95,
    }
    assert summary["overall"]["balanced_accuracy"] == pytest.approx(8 / 9)
    assert summary["overall"]["precision"] == pytest.approx(15 / 17)
    assert summary["overall"]["recall"] == pytest.approx(1.0)
    assert summary["overall"]["discordant_n"] == 2
    assert summary["overall"][
        "spearman_delta_behavior_vs_delta_selective_score"
    ] == pytest.approx(0.9093153287)

    forbidden = {
        "encoder_q90",
        "h1_q90",
        "action_shuffled_h8_q90",
        "action_zeroed_h8_q90",
        "time_shuffled_h8_q90",
    }
    assert forbidden.isdisjoint(rows[0])


def test_generated_cross_task_tables_use_reader_facing_labels() -> None:
    p2_table = (
        ROOT / "paper1/tables/table_cross_task_atr_smpr_all_subsets_v1.tex"
    ).read_text(encoding="utf-8")
    p3_table = (
        ROOT / "paper1/tables/table_cross_stressor_selective_transfer_v1.tex"
    ).read_text(encoding="utf-8")

    assert "Source tasks" in p2_table
    assert "Evaluation tasks" in p2_table
    assert "held-out" not in p2_table.lower()
    assert "Encoder q90" not in p3_table
    assert "H1" not in p3_table
    assert "Correct-action H8" not in p3_table
