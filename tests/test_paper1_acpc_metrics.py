import math
from pathlib import Path
import sys

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.paper1_acpc_metrics import (
    CANONICAL_RADIUS_METRIC,
    MEAN_AGGREGATION_SEMANTICS,
    compute_acpc_horizon_metrics,
    horizon_weighted_stacked_l2,
    per_anchor_clean_transition_scale,
    stepwise_rollout_q90,
    uniform_horizon_weights,
    weighted_stacked_rollout,
)


def test_weighted_stacked_horizon_l2_matches_hand_calculation():
    clean = torch.zeros((1, 2, 2), dtype=torch.float64)
    noisy = torch.tensor([[[1.0, 2.0], [3.0, 4.0]]], dtype=torch.float64)

    radius = horizon_weighted_stacked_l2(
        clean, noisy, weights=torch.tensor([0.25, 0.75], dtype=torch.float64)
    )

    expected = math.sqrt(0.25 * (1.0**2 + 2.0**2) + 0.75 * (3.0**2 + 4.0**2))
    torch.testing.assert_close(radius, torch.tensor([expected], dtype=torch.float64))


def test_default_horizon_weights_are_uniform_and_use_sqrt_alpha():
    weights = uniform_horizon_weights(4, dtype=torch.float64)
    torch.testing.assert_close(weights, torch.full((4,), 0.25, dtype=torch.float64))

    rollout = torch.tensor([[[2.0], [4.0]]], dtype=torch.float64)
    stacked = weighted_stacked_rollout(rollout)
    expected = torch.tensor(
        [[2.0 / math.sqrt(2.0), 4.0 / math.sqrt(2.0)]], dtype=torch.float64
    )
    torch.testing.assert_close(stacked, expected)


def test_clean_transition_normalization_is_per_anchor():
    clean = torch.tensor(
        [
            [[0.0], [2.0], [4.0]],
            [[0.0], [4.0], [8.0]],
        ],
        dtype=torch.float64,
    )
    noisy = clean + 2.0

    scales = per_anchor_clean_transition_scale(clean)
    result = compute_acpc_horizon_metrics(clean, noisy, eps=1e-12)

    torch.testing.assert_close(scales, torch.tensor([2.0, 4.0], dtype=torch.float64))
    torch.testing.assert_close(result["clean_transition_scale"], scales)
    torch.testing.assert_close(
        result["horizon_radius_per_anchor"],
        torch.tensor([1.0, 0.5], dtype=torch.float64),
        rtol=0.0,
        atol=1e-12,
    )


def test_noise_draws_are_aggregated_within_anchor_before_checkpoint_quantile():
    clean = torch.zeros((2, 1, 1), dtype=torch.float64)
    noisy = torch.tensor(
        [
            [[[1.0]], [[3.0]]],
            [[[5.0]], [[7.0]]],
        ],
        dtype=torch.float64,
    )

    result = compute_acpc_horizon_metrics(
        clean,
        noisy,
        clean_transition_scale=torch.ones(2, dtype=torch.float64),
        noise_draw_dim=1,
        atr_quantile=0.50,
        eps=1e-12,
    )

    torch.testing.assert_close(
        result["horizon_radius_per_noise_draw"],
        torch.tensor([[1.0, 3.0], [5.0, 7.0]], dtype=torch.float64),
        rtol=0.0,
        atol=1e-11,
    )
    torch.testing.assert_close(
        result["horizon_radius_per_anchor"],
        torch.tensor([2.0, 6.0], dtype=torch.float64),
        rtol=0.0,
        atol=1e-11,
    )
    torch.testing.assert_close(result["atr"], torch.tensor(4.0, dtype=torch.float64))
    assert result["noise_draw_aggregation"] == MEAN_AGGREGATION_SEMANTICS


def test_legacy_stepwise_q90_is_distinct_from_horizon_atr():
    clean = torch.zeros((1, 2, 1), dtype=torch.float64)
    noisy = torch.tensor([[[0.0], [2.0]]], dtype=torch.float64)

    result = compute_acpc_horizon_metrics(
        clean,
        noisy,
        clean_transition_scale=torch.ones(1, dtype=torch.float64),
        eps=1e-12,
    )

    torch.testing.assert_close(
        result["atr"],
        torch.tensor(math.sqrt(2.0), dtype=torch.float64),
        rtol=0.0,
        atol=2e-12,
    )
    torch.testing.assert_close(
        result["stepwise_rollout_q90"], torch.tensor(1.8, dtype=torch.float64)
    )
    torch.testing.assert_close(
        result["stepwise_rollout_q90"], stepwise_rollout_q90(clean, noisy)
    )
    assert result["radius_metric"] == CANONICAL_RADIUS_METRIC
    assert result["stepwise_rollout_q90_is_atr"] is False
    assert result["stepwise_rollout_q90"] != result["atr"]


def test_finite_validation_and_eps_keep_zero_scale_well_defined():
    clean = torch.zeros((1, 2, 1), dtype=torch.float64)
    noisy = clean.clone()
    result = compute_acpc_horizon_metrics(
        clean,
        noisy,
        clean_transition_scale=torch.zeros(1, dtype=torch.float64),
    )
    assert torch.isfinite(result["atr"])
    assert result["atr"].item() == 0.0

    with pytest.raises(ValueError, match="eps"):
        compute_acpc_horizon_metrics(
            clean,
            noisy,
            clean_transition_scale=torch.ones(1),
            eps=0.0,
        )
    with pytest.raises(ValueError, match="NaN or infinity"):
        horizon_weighted_stacked_l2(
            clean,
            torch.tensor([[[float("nan")], [0.0]]], dtype=torch.float64),
        )
    with pytest.raises(ValueError, match="sum to 1"):
        weighted_stacked_rollout(clean, weights=[1.0, 1.0])
