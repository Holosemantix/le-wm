from __future__ import annotations

import pytest
import torch

from tools.paper1_acpc_adaptive_cem_audit import (
    compare_adaptive_outputs,
    normalized_action_rms,
    topk_jaccard,
)


def _trace(best: list[int], topk: list[list[int]], mean: torch.Tensor) -> list[dict]:
    batch = len(best)
    # Keep nominal and probe traces on the same frozen candidate pool even when
    # their selected elite indices differ.
    candidate_count = 6
    costs = torch.arange(
        candidate_count, dtype=torch.float32
    ).unsqueeze(0).expand(batch, -1).clone()
    return [
        {
            "costs": costs,
            "best_index": torch.tensor(best),
            "topk_indices": torch.tensor(topk),
            "best_cost": torch.zeros(batch),
            "mean": mean,
            "std": torch.ones_like(mean),
        }
    ]


def test_normalized_action_rms_is_per_dimension_not_vector_length() -> None:
    nominal = torch.zeros(2, 4)
    probe = torch.tensor([[1.0, 1.0, 1.0, 1.0], [2.0, 0.0, 0.0, 0.0]])

    assert normalized_action_rms(nominal, probe).tolist() == pytest.approx([1.0, 1.0])


def test_topk_jaccard_tracks_aligned_crn_indices() -> None:
    nominal = torch.tensor([[0, 1], [2, 3]])
    probe = torch.tensor([[1, 0], [2, 4]])

    assert topk_jaccard(nominal, probe).tolist() == pytest.approx([1.0, 1.0 / 3.0])


def test_adaptive_event_uses_frozen_first_action_tolerance() -> None:
    nominal = torch.zeros(2, 3, 4)
    probe = nominal.clone()
    probe[0, 0] = 0.05
    probe[1, 0] = 0.20
    trace_nominal = _trace([0, 1], [[0, 1], [1, 2]], torch.zeros(2, 3, 4))
    trace_probe = _trace([0, 2], [[1, 0], [2, 3]], torch.ones(2, 3, 4))
    trace_probe[0]["costs"][1] = torch.tensor(
        [5.0, 4.0, 0.0, 1.0, 2.0, 3.0]
    )

    result = compare_adaptive_outputs(
        nominal,
        probe,
        trace_nominal,
        trace_probe,
        first_action_tolerance=0.10,
    )

    assert result["first_action_stable"].tolist() == [True, False]
    assert result["step_rows"][0]["top1_agreement"].tolist() == [True, False]
    assert result["step_rows"][0]["mean_rms_drift"].tolist() == pytest.approx(
        [1.0, 1.0]
    )
    assert result["step_rows"][0]["proposal_aligned_by_induction"].tolist() == [
        True,
        True,
    ]


def test_identity_actions_are_stable_and_trace_comparison_is_exact() -> None:
    actions = torch.randn(3, 5, 2, generator=torch.Generator().manual_seed(3))
    trace = _trace([0, 1, 2], [[0, 1], [1, 2], [2, 3]], torch.zeros(3, 5, 2))

    result = compare_adaptive_outputs(
        actions,
        actions.clone(),
        trace,
        trace,
        first_action_tolerance=0.0,
    )

    assert bool(result["first_action_stable"].all())
    assert bool(result["step_rows"][0]["top1_agreement"].all())
    assert result["step_rows"][0]["elite_jaccard"].tolist() == [1.0, 1.0, 1.0]


def test_invalid_adaptive_shapes_are_rejected() -> None:
    with pytest.raises(ValueError):
        normalized_action_rms(torch.zeros(2, 3), torch.zeros(2, 4))
    with pytest.raises(ValueError):
        topk_jaccard(torch.zeros(2, 3), torch.zeros(2, 3, 1))


def test_aligned_pool_elite_certificate_preserves_distribution() -> None:
    actions = torch.zeros(1, 2, 2)
    nominal_trace = [
        {
            "costs": torch.tensor([[0.0, 0.1, 4.0, 5.0]]),
            "best_index": torch.tensor([0]),
            "topk_indices": torch.tensor([[0, 1]]),
            "best_cost": torch.tensor([0.0]),
            "mean": torch.zeros(1, 2, 2),
            "std": torch.ones(1, 2, 2),
        }
    ]
    probe_trace = [
        {
            **nominal_trace[0],
            "costs": torch.tensor([[0.01, 0.09, 4.01, 4.99]]),
        }
    ]

    result = compare_adaptive_outputs(
        actions,
        actions,
        nominal_trace,
        probe_trace,
        first_action_tolerance=0.1,
    )

    step = result["step_rows"][0]
    assert bool(step["aligned_pool_elite_certificate"].all())
    assert bool(step["elite_membership_same"].all())
    assert bool(step["distribution_update_aligned"].all())
    assert bool(result["all_steps_distribution_aligned"].all())
