from __future__ import annotations

import pytest
import torch

from tools.paper1_acpc_planner_stability_audit import (
    _shared_pool_costs,
    _validate_severities,
    candidate_latent_acpc_metrics,
    choose_unique_episode_indices,
    mse_cost_acpc_metrics,
    tie_aware_decision_metrics,
)


class _ToyCostModel:
    def get_cost(
        self,
        info: dict[str, torch.Tensor],
        candidates: torch.Tensor,
    ) -> torch.Tensor:
        assert info["pixels"].shape[:2] == candidates.shape[:2]
        assert info["action"].shape[:2] == candidates.shape[:2]
        assert info["goal"].shape[:2] == candidates.shape[:2]
        # Candidate expansion has a zero-stride candidate axis, but all model
        # data axes must originate from the same canonical contiguous layout.
        assert info["pixels"].stride()[2:] == (48, 16, 4, 1)
        assert info["action"].stride()[2:] == (2, 1)
        assert info["goal"].stride()[2:] == (48, 16, 4, 1)
        return candidates.float().flatten(2).square().sum(dim=2)


def test_shared_pool_cost_path_is_exact_for_identity_batch() -> None:
    generator = torch.Generator().manual_seed(71)
    contiguous_pixels = torch.randn(3, 5, 3, 4, 4, generator=generator)
    channels_last_pixels = contiguous_pixels.to(
        memory_format=torch.channels_last_3d
    )
    assert torch.equal(contiguous_pixels, channels_last_pixels)
    assert contiguous_pixels.stride() != channels_last_pixels.stride()
    batch = {
        "pixels": channels_last_pixels,
        "action": torch.randn(3, 5, 2, generator=generator),
    }
    candidates = torch.randn(3, 7, 6, 2, generator=generator)
    model = _ToyCostModel()

    nominal = _shared_pool_costs(
        model,
        batch,
        candidates,
        history_size=3,
        device="cpu",
    )
    identity_probe = _shared_pool_costs(
        model,
        {
            "pixels": contiguous_pixels.clone(),
            "action": batch["action"].clone(),
        },
        candidates.clone(),
        history_size=3,
        device="cpu",
    )

    assert torch.equal(nominal, identity_probe)
    metrics = tie_aware_decision_metrics(nominal, identity_probe)
    assert metrics["exact_stable"].all()
    assert torch.count_nonzero(metrics["max_absolute_drift"]) == 0


def test_exact_event_is_stable_with_positive_unique_gap() -> None:
    nominal = torch.tensor([[0.0, 1.0, 2.0]])
    probe = torch.tensor([[0.2, 0.8, 2.5]])

    metrics = tie_aware_decision_metrics(nominal, probe)

    assert metrics["nominal_winner"].tolist() == [0]
    assert metrics["probe_winner"].tolist() == [0]
    assert metrics["exact_stable"].tolist() == [True]
    assert metrics["strict_unique_same_winner"].tolist() == [True]
    assert metrics["min_signed_probe_gap"].tolist() == pytest.approx([0.6])


def test_exact_event_detects_changed_winner() -> None:
    nominal = torch.tensor([[0.0, 0.5, 2.0]])
    probe = torch.tensor([[0.8, 0.2, 2.1]])

    metrics = tie_aware_decision_metrics(nominal, probe)

    assert metrics["nominal_winner"].tolist() == [0]
    assert metrics["probe_winner"].tolist() == [1]
    assert metrics["exact_stable"].tolist() == [False]
    assert metrics["strict_unique_same_winner"].tolist() == [False]
    assert metrics["min_signed_probe_gap"].item() < 0.0


def test_ordered_tie_can_be_stable_without_strict_certificate() -> None:
    nominal = torch.tensor([[0.0, 1.0, 2.0]])
    probe = torch.tensor([[0.5, 0.5, 2.0]])

    metrics = tie_aware_decision_metrics(nominal, probe)

    assert metrics["exact_stable"].tolist() == [True]
    assert metrics["strict_unique_same_winner"].tolist() == [False]
    assert metrics["probe_tie_count"].tolist() == [2]
    assert metrics["min_signed_probe_gap"].tolist() == pytest.approx([0.0])


def test_ordered_tie_changes_winner_when_earlier_candidate_ties() -> None:
    nominal = torch.tensor([[1.0, 0.0, 2.0]])
    probe = torch.tensor([[0.5, 0.5, 2.0]])

    metrics = tie_aware_decision_metrics(nominal, probe)

    assert metrics["nominal_winner"].tolist() == [1]
    assert metrics["probe_winner"].tolist() == [0]
    assert metrics["exact_stable"].tolist() == [False]
    assert metrics["min_signed_probe_gap"].tolist() == pytest.approx([0.0])


def test_signed_gap_identity_matches_direct_probe_gap() -> None:
    generator = torch.Generator().manual_seed(17)
    nominal = torch.randn(7, 11, generator=generator)
    probe = torch.randn(7, 11, generator=generator)

    metrics = tie_aware_decision_metrics(nominal, probe)
    winner = metrics["nominal_winner"]
    expected = []
    for row, winner_index in zip(probe, winner, strict=True):
        competitor = torch.cat((row[:winner_index], row[winner_index + 1 :]))
        expected.append(float((competitor - row[winner_index]).min()))

    assert metrics["min_signed_probe_gap"].tolist() == pytest.approx(expected)


@pytest.mark.parametrize(
    ("nominal", "probe"),
    [
        (torch.tensor([0.0, 1.0]), torch.tensor([0.0, 1.0])),
        (torch.zeros(2, 3), torch.zeros(2, 4)),
        (torch.tensor([[0.0, float("nan")]]), torch.zeros(1, 2)),
    ],
)
def test_invalid_cost_tensors_are_rejected(
    nominal: torch.Tensor,
    probe: torch.Tensor,
) -> None:
    with pytest.raises(ValueError):
        tie_aware_decision_metrics(nominal, probe)


def test_mse_cost_acpc_bound_and_top1_elite_certificates() -> None:
    goal = torch.zeros(1, 2)
    nominal_z = torch.tensor([[[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]])
    probe_z = torch.tensor([[[0.0, 0.0], [1.1, 0.0], [2.1, 0.0]]])
    nominal_costs = nominal_z.square().sum(dim=-1)
    probe_costs = probe_z.square().sum(dim=-1)

    result = mse_cost_acpc_metrics(
        nominal_costs,
        probe_costs,
        nominal_z,
        probe_z,
        goal,
        topk=2,
    )

    assert bool(result["all_mse_bounds_hold"].all())
    assert bool(result["acpc_top1_certificate"].all())
    assert bool(result["acpc_elite_certificate"].all())
    assert bool(result["exact_elite_set_stable"].all())
    assert result["elite_jaccard"].tolist() == [1.0]


def test_mse_cost_acpc_certificate_abstains_when_bound_crosses_margin() -> None:
    goal = torch.zeros(1, 1)
    nominal_z = torch.tensor([[[0.0], [0.2], [1.0]]])
    probe_z = torch.tensor([[[0.3], [0.0], [1.0]]])
    nominal_costs = nominal_z.square().sum(dim=-1)
    probe_costs = probe_z.square().sum(dim=-1)

    result = mse_cost_acpc_metrics(
        nominal_costs,
        probe_costs,
        nominal_z,
        probe_z,
        goal,
        topk=1,
    )

    assert bool(result["all_mse_bounds_hold"].all())
    assert not bool(result["acpc_top1_certificate"].any())
    assert not bool(result["exact_elite_set_stable"].any())


def test_candidate_latent_acpc_summary_is_candidate_conditioned() -> None:
    nominal = torch.zeros(2, 3, 2)
    probe = nominal.clone()
    probe[0, 1] = torch.tensor([3.0, 4.0])
    probe[1] = 1.0

    result = candidate_latent_acpc_metrics(nominal, probe)

    assert result["max_candidate_acpc_l2"].tolist() == pytest.approx(
        [5.0, 2.0**0.5]
    )
    assert result["mean_candidate_acpc_l2"].tolist() == pytest.approx(
        [5.0 / 3.0, 2.0**0.5]
    )


def test_unique_episode_sampler_is_deterministic_and_block_independent() -> None:
    clip_indices = [
        (10, 0),
        (10, 5),
        (11, 0),
        (11, 5),
        (12, 0),
        (13, 0),
        (14, 0),
    ]

    first = choose_unique_episode_indices(clip_indices, n_blocks=4, seed=123)
    second = choose_unique_episode_indices(clip_indices, n_blocks=4, seed=123)

    assert first == second
    assert len({episode for _index, episode, _start in first}) == 4
    for dataset_index, episode, start in first:
        assert clip_indices[dataset_index] == (episode, start)


def test_unique_episode_sampler_rejects_pseudoreplication() -> None:
    with pytest.raises(ValueError, match="only 2 episodes"):
        choose_unique_episode_indices(
            [(1, 0), (1, 5), (2, 0)],
            n_blocks=3,
            seed=1,
        )


@pytest.mark.parametrize(
    ("family", "values"),
    [
        ("gaussian_noise", [0.0, 0.02, 0.04]),
        ("gaussian_blur", [1.0, 3.0, 5.0]),
        ("resize", [1.0, 0.75, 0.5]),
    ],
)
def test_probe_severity_grids_are_identity_first_and_ordered(
    family: str,
    values: list[float],
) -> None:
    assert _validate_severities(family, values) == values


@pytest.mark.parametrize(
    ("family", "values"),
    [
        ("gaussian_noise", [0.01, 0.02]),
        ("gaussian_blur", [1.0, 5.0, 3.0]),
        ("resize", [1.0, 0.5, 0.75]),
        ("resize", [1.0, 1.0]),
    ],
)
def test_invalid_probe_severity_grids_are_rejected(
    family: str,
    values: list[float],
) -> None:
    with pytest.raises(ValueError):
        _validate_severities(family, values)
