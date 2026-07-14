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


def test_future_drift_text_describes_all_three_destroyed_action_controls() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    assert "strongest of three same-horizon destroyed-action controls" in text
    assert "zeroed actions, actions from another trajectory, or time-shuffled actions" in text
    assert "better of the two" not in text


def test_main_text_uses_reader_facing_data_flow_language() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    lowered = text.lower()

    for excluded in (
        "seed3075",
        "seed 3075",
        "dev-era",
        "prospective seed",
        "correct-action",
        "table_cross_stressor_robustness_audit",
        "table_seed_transfer_audit",
    ):
        assert excluded not in lowered

    assert "absolute change in eight-step latent prediction error" in lowered
    assert "this gives 14 directional" in lowered
    assert "selected from one, two, and three source tasks" in lowered
    assert "action-conditioned predictive consistency" in lowered
    assert "task-proxy margin" in lowered
    assert "checkpoint-level calibration" in lowered


def test_theory_section_contains_the_complete_radius_margin_chain() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    body = text.split(r"\section{Experiments}", 1)[0]

    headings = (
        r"\subsection{Paired rollout radius}",
        r"\subsection{Common-future error drift}",
        r"\subsection{Candidate-cost drift and planner stability}",
        r"\subsection{Why low radius needs a task-proxy margin}",
        r"\subsection{Checkpoint-level calibration}",
    )
    assert [body.index(heading) for heading in headings] == sorted(
        body.index(heading) for heading in headings
    )

    for label in (
        r"\label{eq:acpc-rollout-objects}",
        r"\label{eq:weighted-rollout-map}",
        r"\label{eq:normalized-same-state-radius}",
        r"\label{eq:atr-raw}",
        r"\label{eq:different-state-distance}",
        r"\label{eq:smpr}",
        r"\label{eq:atr-relative}",
        r"\label{eq:joint-diagnostic-score}",
    ):
        assert label in body

    assert r"\mathrm{ATR}^{\mathrm{raw}}_q(\theta)+\delta" in body
    assert "q35 of all off-diagonal Euclidean distances" in body
    assert "normalized margin $\\delta=0.10$" in body
    assert "SMPR is the fraction of tested proxy-different pairs" in body
    assert r"\begin{proposition}" in body
    assert r"\begin{theorem}" not in body
    assert "thm:" not in body


def test_smpr_proxy_descriptions_match_the_executed_coordinate_slices() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    correction = json.loads(
        (
            ROOT
            / "paper1/results/smpr_v2_proxy_metadata_correction_v1.json"
        ).read_text()
    )

    assert correction["numeric_rows_unchanged"] is True
    assert correction["pair_indices_unchanged"] is True
    assert "observation[4:6]" in correction["implemented_proxy_labels"]["Reacher"][
        "definition"
    ]
    assert "o[0:3]-o[25:28]" in correction["implemented_proxy_labels"]["Cube"][
        "definition"
    ]
    assert r"\code{observation[4:6]}" in text
    assert r"\bar o_{0:3}-\bar o_{25:28}" in text
    assert "Target--end-effector relation" not in text
    assert "Cube--goal relation" not in text
    assert "not semantic or action-relevance annotations" in text


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
