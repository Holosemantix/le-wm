from __future__ import annotations

import pytest
import torch

from tools.paper1_semantic_margin import compute_smpr_v2_from_rollouts


def test_smpr_v2_aggregates_draws_before_checkpoint_tube_quantile() -> None:
    clean = torch.zeros((2, 2, 1), dtype=torch.float64)
    noisy = torch.tensor(
        [
            [[[1.0], [1.0]], [[3.0], [3.0]]],
            [[[4.0], [4.0]], [[6.0], [6.0]]],
        ],
        dtype=torch.float64,
    )
    different = torch.tensor(
        [[[4.0], [4.0]], [[3.0], [3.0]]],
        dtype=torch.float64,
    )

    result = compute_smpr_v2_from_rollouts(
        clean_rollout=clean,
        noisy_rollout=noisy,
        different_state_rollout=different,
        pair_anchor_indices=torch.tensor([0, 1]),
        clean_transition_scale=torch.ones(2, dtype=torch.float64),
        radius_quantile=0.50,
        margin_delta_norm=0.10,
        eps=1e-12,
    )

    torch.testing.assert_close(
        result["same_state_radius_per_noise_draw"],
        torch.tensor([[1.0, 3.0], [4.0, 6.0]], dtype=torch.float64),
    )
    torch.testing.assert_close(
        result["same_state_radius_per_anchor"],
        torch.tensor([2.0, 5.0], dtype=torch.float64),
    )
    torch.testing.assert_close(
        result["same_state_tube_radius"],
        torch.tensor(3.5, dtype=torch.float64),
    )
    torch.testing.assert_close(
        result["different_state_distance_per_pair"],
        torch.tensor([4.0, 3.0], dtype=torch.float64),
    )
    assert result["pair_pass"].tolist() == [True, False]
    assert result["smpr"].item() == pytest.approx(0.5)
    assert result["noise_draw_aggregation"] == (
        "per_anchor_mean_then_checkpoint_radius_quantile"
    )


def test_smpr_v2_uses_each_anchor_clean_transition_scale() -> None:
    clean = torch.zeros((2, 2, 1), dtype=torch.float64)
    noisy = clean.unsqueeze(1)
    different = torch.full((2, 2, 1), 2.0, dtype=torch.float64)

    result = compute_smpr_v2_from_rollouts(
        clean_rollout=clean,
        noisy_rollout=noisy,
        different_state_rollout=different,
        pair_anchor_indices=torch.tensor([0, 1]),
        clean_transition_scale=torch.tensor([1.0, 4.0], dtype=torch.float64),
        margin_delta_norm=1.0,
        eps=1e-12,
    )

    torch.testing.assert_close(
        result["different_state_distance_per_pair"],
        torch.tensor([2.0, 0.5], dtype=torch.float64),
    )
    assert result["pair_pass"].tolist() == [True, False]


def test_smpr_v2_positive_margin_rejects_constant_collapse() -> None:
    clean = torch.zeros((1, 2, 1), dtype=torch.float64)
    result = compute_smpr_v2_from_rollouts(
        clean_rollout=clean,
        noisy_rollout=clean.unsqueeze(1).expand(-1, 2, -1, -1),
        different_state_rollout=clean.clone(),
        pair_anchor_indices=torch.tensor([0]),
        clean_transition_scale=torch.ones(1, dtype=torch.float64),
        margin_delta_norm=0.10,
    )

    assert result["same_state_tube_radius"].item() == pytest.approx(0.0)
    assert result["different_state_distance_per_pair"].item() == pytest.approx(0.0)
    assert result["pair_pass"].tolist() == [False]
    assert result["smpr"].item() == pytest.approx(0.0)


def test_smpr_v2_identical_clean_noisy_positive_control() -> None:
    clean = torch.zeros((1, 2, 1), dtype=torch.float64)
    different = torch.full_like(clean, 0.2)
    result = compute_smpr_v2_from_rollouts(
        clean_rollout=clean,
        noisy_rollout=clean.unsqueeze(1).expand(-1, 2, -1, -1),
        different_state_rollout=different,
        pair_anchor_indices=torch.tensor([0]),
        clean_transition_scale=torch.ones(1, dtype=torch.float64),
        margin_delta_norm=0.10,
    )

    assert result["pair_pass"].tolist() == [True]
    assert result["smpr"].item() == pytest.approx(1.0)


def test_smpr_v2_rejects_invalid_pair_mapping() -> None:
    clean = torch.zeros((1, 2, 1), dtype=torch.float64)
    with pytest.raises(ValueError, match="out-of-range"):
        compute_smpr_v2_from_rollouts(
            clean_rollout=clean,
            noisy_rollout=clean.unsqueeze(1),
            different_state_rollout=clean.clone(),
            pair_anchor_indices=torch.tensor([1]),
            clean_transition_scale=torch.ones(1, dtype=torch.float64),
        )
