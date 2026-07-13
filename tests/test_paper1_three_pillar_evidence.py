from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper1.scripts.build_three_pillar_evidence import (
    _classification_metrics,
    _clopper_pearson_interval,
    _one_sided_binomial_upper,
)
from paper1.scripts.summarize_target_aligned_acpc_four_task import (
    _one_sided_sign_p_value,
)


ROOT = Path(__file__).resolve().parents[1]


def test_classification_metrics_match_confusion_definition() -> None:
    rows = [
        {"behavior_label": True, "frozen_gate_pass": True, "joint_score": 3},
        {"behavior_label": True, "frozen_gate_pass": False, "joint_score": 2},
        {"behavior_label": False, "frozen_gate_pass": True, "joint_score": 1},
        {"behavior_label": False, "frozen_gate_pass": False, "joint_score": 0},
    ]

    metrics = _classification_metrics(rows)

    assert metrics["tp"] == metrics["tn"] == 1
    assert metrics["fp"] == metrics["fn"] == 1
    assert metrics["balanced_accuracy"] == pytest.approx(0.5)
    assert metrics["precision"] == pytest.approx(0.5)
    assert metrics["recall"] == pytest.approx(0.5)
    assert metrics["specificity"] == pytest.approx(0.5)
    assert metrics["auprc"] == pytest.approx(1.0)


def test_exact_one_sided_sign_probability() -> None:
    assert _one_sided_sign_p_value(4, 4) == pytest.approx(1 / 16)
    assert _one_sided_sign_p_value(2, 4) == pytest.approx(11 / 16)


def test_exact_binomial_bounds_cover_zero_false_pass_case() -> None:
    assert _one_sided_binomial_upper(0, 7) == pytest.approx(
        0.34816365513116077
    )
    assert _clopper_pearson_interval(7, 24) == pytest.approx(
        [0.12615208852369136, 0.5109478138578332]
    )


def test_generated_three_pillar_bundle_preserves_claim_boundaries() -> None:
    path = ROOT / "paper1/results/three_pillar_evidence_summary.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["metadata"]["schema_version"] == (
        "paper1-three-pillar-evidence-1.0"
    )
    assert payload["metadata"]["threshold_search_allowed"] is False
    assert payload["metadata"]["model_evaluation_performed"] is False

    p1 = payload["P1"]["primary_logged_fragile_base"]
    assert p1["all_available_seeds_pass_all_four_tasks"] is True
    assert p1["uncertainty"]["absolute"]["paired_block_direction"][
        "both_win_count"
    ] == 57
    assert p1["uncertainty"]["absolute"]["paired_block_direction"][
        "cluster_count"
    ] == 64

    p2 = payload["P2"]
    assert p2["threshold_search_allowed"] is False
    assert p2["overall"]["n"] == 72
    assert p2["overall"]["balanced_accuracy"] == pytest.approx(
        0.9445454545454546
    )
    assert p2["onset_error"]["maximum_absolute"] == pytest.approx(0.01)

    p3 = payload["P3"]
    assert p3["threshold_search_allowed"] is False
    assert p3["absolute_single_checkpoint_screen"]["precision"] == 1.0
    assert p3["absolute_single_checkpoint_screen"]["recall"] < 0.5
    assert p3["absolute_single_checkpoint_screen"]["coverage"][
        "pass_count"
    ] == 7
    assert p3["absolute_single_checkpoint_screen"][
        "selective_false_pass_risk"
    ]["exact_one_sided_95_upper"] == pytest.approx(0.34816365513116077)
    assert "pair-derived positive transfer" in p3[
        "absolute_single_checkpoint_screen"
    ]["evaluation_target"]
    assert "not an absolute stability label" in p3["boundary"]
    assert "reference checkpoint" in p3["boundary"]
