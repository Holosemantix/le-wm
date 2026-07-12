from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper1.scripts.build_cross_stressor_external_validation import (
    _average_precision,
    _classification,
    _delta_metric_summary,
    _quantile,
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
