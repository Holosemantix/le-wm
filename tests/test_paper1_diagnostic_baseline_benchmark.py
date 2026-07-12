from pathlib import Path
import sys

import pytest
import torch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper1.scripts.diagnostic_baseline_benchmark import _canonical_q90, _resolve_checkpoint
from paper1.scripts.build_diagnostic_baseline_artifact import _select_threshold


def test_baseline_q90_uses_per_anchor_scale_and_draw_before_quantile():
    clean = torch.zeros((2, 1, 1), dtype=torch.float64)
    noisy = torch.tensor(
        [
            [[[1.0]], [[3.0]]],
            [[[2.0]], [[6.0]]],
        ],
        dtype=torch.float64,
    )

    value = _canonical_q90(
        clean,
        noisy,
        clean_transition_scale=torch.tensor([2.0, 4.0], dtype=torch.float64),
        eps=1e-12,
    )

    # Per-anchor draw means are both 1, so every checkpoint quantile is 1.
    assert value == pytest.approx(1.0)


def test_checkpoint_binding_falls_back_to_legacy_reference_model_file(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    checkpoint = run / "model_epoch_10_object.ckpt"
    checkpoint.write_bytes(b"checkpoint")

    resolved, digest, source = _resolve_checkpoint(
        {"path": str(run), "subdir": "run"},
        {"model_file": str(checkpoint)},
        [tmp_path],
        name="legacy-cal-row",
    )

    assert resolved == checkpoint.resolve()
    assert len(digest) == 64
    assert source == "reference_model_file_sha256"


def test_checkpoint_binding_rejects_legacy_reference_mismatch(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    checkpoint = run / "model_epoch_10_object.ckpt"
    checkpoint.write_bytes(b"checkpoint")
    other = tmp_path / "reference.ckpt"
    other.write_bytes(b"different")

    with pytest.raises(ValueError, match="checkpoint hash mismatch"):
        _resolve_checkpoint(
            {"path": str(run), "subdir": "run"},
            {"model_file": str(other)},
            [tmp_path],
            name="legacy-cal-row",
        )


def test_high_is_positive_calibration_direction_is_respected():
    rows = [
        {"clean_score": 1.0, "behavior_label": False},
        {"clean_score": 2.0, "behavior_label": False},
        {"clean_score": 8.0, "behavior_label": True},
        {"clean_score": 9.0, "behavior_label": True},
    ]
    selected = _select_threshold(
        rows,
        "clean_score",
        direction="pass_if_value_ge_threshold",
    )

    assert selected["direction"] == "pass_if_value_ge_threshold"
    assert 2.0 < selected["threshold"] < 8.0
    assert selected["calibration_balanced_accuracy"] == pytest.approx(1.0)
