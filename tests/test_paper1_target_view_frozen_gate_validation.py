from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper1.scripts.target_view_frozen_gate_validation import (
    _average_precision,
    _joint,
    _preference,
)


def test_frozen_joint_score_is_minimum_normalized_margin():
    score, passed = _joint(
        atr=1.0,
        smpr=0.95,
        tau_atr=2.0,
        tau_smpr=0.5,
    )
    assert score == pytest.approx(0.5)
    assert passed is True


def test_matched_preference_preserves_ties():
    assert _preference(1.0, 1.0, left_name="full", right_name="target") == "tie"
    assert _preference(2.0, 1.0, left_name="full", right_name="target") == "full"
    assert _preference(1.0, 2.0, left_name="full", right_name="target") == "target"


def test_tie_aware_auprc_does_not_order_within_equal_scores():
    assert _average_precision(
        [True, False, True, False],
        [1.0, 1.0, 0.0, 0.0],
    ) == pytest.approx(0.5)
