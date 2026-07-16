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
    expected_metrics = {
        1: (0.8545304233, 0.9102513228, 0.8539682540, 0.0108333333),
        2: (0.8996031746, 0.9126984127, 0.9533730159, 0.005),
        3: (0.8996031746, 0.9126984127, 0.9533730159, 0.005),
    }
    for coverage, (balanced_accuracy, precision, recall, onset_error) in (
        expected_metrics.items()
    ):
        row = by_coverage[coverage]
        assert row["balanced_accuracy"] == pytest.approx(balanced_accuracy)
        assert row["precision"] == pytest.approx(precision)
        assert row["recall"] == pytest.approx(recall)
        assert row["mean_abs_start_error"] == pytest.approx(onset_error)

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

    assert params["diagnostic_fields"] == {
        "atr": "horizon-v2 q90 relative to the no-augmentation checkpoint",
        "smpr": "horizon-v2 q90 tube with strict normalized margin 0.10",
    }
    assert {
        (
            split["selected_thresholds"]["tau_atr"],
            split["selected_thresholds"]["tau_smpr"],
        )
        for split in params["splits"]
        if split["source_coverage"] == 3
    } == {(0.3, 0.95)}


def test_paper_facing_full_sweep_is_bound_to_canonical_v2_atr_smpr() -> None:
    calibration = json.loads(
        (ROOT / "paper1/results/frozen_diagnostic_protocol_calibration.json").read_text(
            encoding="utf-8"
        )
    )["calibration_rows"]
    external = json.loads(
        (
            ROOT
            / "paper1/results/external_validation/lewm_heldout_diagnostic_input_v4.json"
        ).read_text(encoding="utf-8")
    )["rows"]
    canonical = {
        (row["task"], int(row["training_seed"]), f"{float(row['training_rho']):.2f}"): (
            float(row["atr_horizon_v2_q90"]),
            float(row["smpr"]),
        )
        for row in [*calibration, *external]
        if row.get("status", "ok") == "ok"
    }

    rows = read_csv(ROOT / "paper1/results/full_sweep_diagnostics.csv")
    assert len(rows) == len(canonical) == 108
    observed_keys = set()
    for row in rows:
        key = (row["task"], int(row["training_seed"]), row["rho"])
        observed_keys.add(key)
        raw_atr, smpr = canonical[key]
        assert float(row["atr_q90"]) == pytest.approx(raw_atr)
        assert float(row["same_radius_q90"]) == pytest.approx(raw_atr)
        assert float(row["smpr_delta010"]) == pytest.approx(smpr)
        assert row["smpr_delta0"] == ""
        assert row["smpr_delta005"] == ""
    assert observed_keys == set(canonical)

    for script_name in (
        "plot_full_sweep_diagnostics.py",
        "cross_task_selective_rule.py",
        "build_acpc_submission_assets.py",
    ):
        script = (ROOT / "paper1/scripts" / script_name).read_text(encoding="utf-8")
        assert "smpr_delta010" in script
        assert '"smpr_delta0"' not in script
        assert "'smpr_delta0'" not in script


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
    assert set(summary["task_thresholds"]) == {"TwoRoom", "PushT", "Reacher", "Cube"}
    assert all(
        thresholds == {"tau_atr": 0.3, "tau_smpr": 0.95}
        for thresholds in summary["task_thresholds"].values()
    )
    assert summary["overall"]["balanced_accuracy"] == pytest.approx(8 / 9)
    assert summary["overall"]["precision"] == pytest.approx(15 / 17)
    assert summary["overall"]["recall"] == pytest.approx(1.0)
    assert summary["overall"]["discordant_n"] == 2
    assert summary["overall"][
        "spearman_delta_behavior_vs_delta_selective_score"
    ] == pytest.approx(0.8352554297)
    assert summary["by_stressor"]["blur"]["balanced_accuracy"] == pytest.approx(0.875)
    assert summary["by_stressor"]["resize"]["balanced_accuracy"] == pytest.approx(0.9)

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

    assert "Selection tasks" in p2_table
    assert "Test tasks" in p2_table
    assert "held-out" not in p2_table.lower()
    assert "Encoder q90" not in p3_table
    assert "H1" not in p3_table
    assert "Correct-action H8" not in p3_table
