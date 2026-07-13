from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper1.scripts.build_cross_stressor_external_validation import (
    _average_precision,
    _classification,
    _delta_metric_summary,
    _exact_binomial_upper_tail,
    _exact_randomization_audit,
    _quantile,
    _selection_summary,
    classify_transfer,
)


RULE = {
    "positive_delta_pp": 5.0,
    "neutral_band_pp": 5.0,
    "max_clean_drop_pp": 5.0,
}


@pytest.mark.parametrize(
    ("delta", "clean_drop", "expected"),
    [
        (5.0, 5.0, "positive"),
        (4.999, 5.0, "neutral"),
        (-4.999, 5.0, "neutral"),
        (-5.0, 5.0, "negative"),
        (20.0, 5.001, "negative"),
    ],
)
def test_external_behavior_label_boundaries_are_pre_registered(delta, clean_drop, expected):
    assert (
        classify_transfer(
            delta_behavior=delta,
            clean_score_drop=clean_drop,
            **RULE,
        )
        == expected
    )


def test_tie_aware_average_precision_enters_equal_scores_together():
    labels = [True, False, True, False]
    scores = [1.0, 1.0, 0.0, 0.0]

    # First tied retrieval set: precision 1/2 at recall 1/2.
    # Second tied retrieval set: precision 2/4 at recall 1.
    assert _average_precision(labels, scores) == pytest.approx(0.5)


def test_binary_metrics_treat_non_positive_transfer_as_negative():
    result = _classification(
        [True, False, False, True],
        [True, True, False, False],
    )

    assert result["tp"] == 1
    assert result["tn"] == 1
    assert result["fp"] == 1
    assert result["fn"] == 1
    assert result["balanced_accuracy"] == pytest.approx(0.5)


def test_paired_change_uses_one_zero_threshold_and_orients_radius_improvement():
    rows = [
        {
            "positive_transfer_label": True,
            "delta_behavior": 10.0,
            "delta_atr": -2.0,
        },
        {
            "positive_transfer_label": False,
            "delta_behavior": -10.0,
            "delta_atr": 1.0,
        },
    ]

    result = _delta_metric_summary(
        rows,
        field="delta_atr",
        direction=-1.0,
    )

    assert result["decision_threshold"] == 0.0
    assert result["balanced_accuracy"] == pytest.approx(1.0)
    assert result["auprc"] == pytest.approx(1.0)
    assert result[
        "spearman_delta_behavior_vs_oriented_delta_score"
    ] == pytest.approx(1.0)
    assert result[
        "signed_agreement_delta_behavior_vs_oriented_delta_score"
    ] == pytest.approx(1.0)


def test_quantile_uses_linear_interpolation():
    assert _quantile([0.0, 10.0], 0.25) == pytest.approx(2.5)


def test_selection_audit_reports_choice_accuracy_and_regret_without_fitting():
    rows = [
        {
            "delta_behavior": 10.0,
            "delta_joint_score": 2.0,
            "base_stressed_score": 50.0,
            "endpoint_stressed_score": 60.0,
        },
        {
            "delta_behavior": -5.0,
            "delta_joint_score": 1.0,
            "base_stressed_score": 70.0,
            "endpoint_stressed_score": 65.0,
        },
    ]

    result = _selection_summary(
        rows,
        field="delta_joint_score",
        direction=1.0,
    )

    assert result["choice_accuracy"] == pytest.approx(0.5)
    assert result["material_choice_accuracy"] == pytest.approx(0.5)
    assert result["mean_regret_pp"] == pytest.approx(2.5)
    assert result["max_regret_pp"] == pytest.approx(5.0)
    assert result["zero_regret_rate"] == pytest.approx(0.5)


def test_exact_randomization_retains_blur_and_resize_within_block():
    rows = [
        {
            "model_family": "LeWM",
            "task": "TaskA",
            "training_seed_or_family_id": "seed1",
            "stressor_family": "blur",
            "delta_behavior": 10.0,
            "delta_joint_score": 2.0,
        },
        {
            "model_family": "LeWM",
            "task": "TaskA",
            "training_seed_or_family_id": "seed1",
            "stressor_family": "resize",
            "delta_behavior": 8.0,
            "delta_joint_score": 1.0,
        },
        {
            "model_family": "LeWM",
            "task": "TaskB",
            "training_seed_or_family_id": "seed2",
            "stressor_family": "blur",
            "delta_behavior": -10.0,
            "delta_joint_score": -2.0,
        },
        {
            "model_family": "LeWM",
            "task": "TaskB",
            "training_seed_or_family_id": "seed2",
            "stressor_family": "resize",
            "delta_behavior": -8.0,
            "delta_joint_score": -1.0,
        },
    ]

    result = _exact_randomization_audit(rows)

    assert result["block_count"] == 2
    assert result["enumerated_assignments"] == 4
    assert result["observed_spearman"] == pytest.approx(1.0)
    assert result["one_sided_p_value"] == pytest.approx(0.25)
    assert result["row_level_signed_agreement"]["successes"] == 4


def test_exact_binomial_tail_is_not_normal_approximation():
    assert _exact_binomial_upper_tail(3, 4) == pytest.approx(5.0 / 16.0)


@pytest.mark.parametrize(
    "transform",
    [
        lambda value: value,
        lambda value: 3.0 * value + 7.0,
        lambda value: value**3,
    ],
)
def test_paired_order_is_invariant_to_strictly_increasing_reparameterization(transform):
    base = 1.0
    endpoint = 2.0
    assert (endpoint - base > 0.0) == (transform(endpoint) - transform(base) > 0.0)
