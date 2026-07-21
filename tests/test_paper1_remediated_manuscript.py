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


def test_future_drift_text_describes_nested_models_and_all_action_controls() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    normalized = " ".join(text.split())
    assert "Every model contains the probe severity and the encoder-history distance" in normalized
    assert r"\emph{zeroed} actions" in normalized
    assert r"\emph{swapped} actions" in normalized
    assert r"\emph{shuffled} actions" in normalized
    assert (
        "the only feature whose action sequence is the one that generated"
        in normalized
    )
    assert "``Strongest'' is an oracle choice" in normalized
    assert "the unaugmented checkpoint of each task and training run" in normalized
    assert "actions from another trajectory" not in normalized
    assert "better of the two" not in normalized


def test_future_drift_figure_names_the_estimand_and_feature_sets() -> None:
    script = (
        ROOT / "paper1/scripts/build_future_drift_reader_display.py"
    ).read_text()
    assert "Regression MAE" in script
    assert "per-cell oracle" in script
    assert "error drift $d$" in script
    assert r"baseline = recorded-action ACPC$_1$" in script
    assert r"oracle control = $+$ best-of-three ACPC$_8$ control" in script
    assert r"recorded = $+$ recorded-action ACPC$_8$" in script
    assert "chosen by the per-cell oracle" in script
    assert "Held-out MAE" not in script


def test_future_drift_appendix_tables_avoid_internal_shorthand() -> None:
    combined = "\n".join(
        (ROOT / path).read_text()
        for path in (
            "paper1/tables/table_target_aligned_acpc.tex",
            "paper1/tables/table_target_aligned_acpc_absolute.tex",
        )
    )
    assert "error drift $d$" in combined
    assert "per-cell oracle" in combined
    assert "encoder response" not in combined
    assert "H8" not in combined
    assert "oracle" in combined


def test_main_text_uses_reader_facing_data_flow_language() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    lowered = text.lower()
    normalized = " ".join(lowered.split())

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

    assert "error drift $d=|e_{\\tilde h}-e_h|$" in normalized
    assert "held-out mae" not in lowered
    assert "produce $4+6+4=14$ directional" in normalized
    assert "the one-, two-, and three-task selection settings" in normalized
    assert "action-conditioned predictive consistency" in lowered
    assert "ir and dr for checkpoint screening" in lowered
    assert "checkpoint-level threshold selection" in lowered


def test_theory_section_contains_the_complete_radius_margin_chain() -> None:
    text = (ROOT / "paper1/main.tex").read_text()
    body = text.split(r"\section{Experiments}", 1)[0]

    headings = (
        r"\subsection{Pairwise ACPC}",
        r"\subsection{Common-future error drift}",
        r"\subsection{Candidate-cost drift and planner stability}",
        r"\subsection{IR and DR for checkpoint screening}",
        r"\subsection{Checkpoint-level threshold selection}",
    )
    assert [body.index(heading) for heading in headings] == sorted(
        body.index(heading) for heading in headings
    )

    for label in (
        r"\label{eq:acpc-rollout-objects}",
        r"\label{eq:weighted-rollout-map}",
        r"\label{eq:normalized-same-state-radius}",
        r"\label{eq:ir-raw}",
        r"\label{eq:dr}",
        r"\label{eq:ir-relative}",
        r"\label{eq:ir-dr-score}",
    ):
        assert label in body

    assert r"\mathrm{IR}^{\mathrm{raw}}_q(\theta)+\delta" in body
    assert "normalized margin $\\delta=0.10$" in body
    assert "DR is the fraction of tested different-label pairs" in body
    assert r"\label{eq:different-state-distance}" in text
    assert "q35 of all off-diagonal Euclidean distances" in text
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
        ROOT / "paper1/tables/table_cross_stressor_ir_dr_summary_v1.tex"
    ).read_text()
    all_pairs_table = (
        ROOT / "paper1/tables/table_cross_stressor_ir_dr_all_pairs_v1.tex"
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
