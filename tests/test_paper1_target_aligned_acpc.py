from __future__ import annotations

import numpy as np
import pytest
import torch
from sklearn.preprocessing import StandardScaler

from tools import paper1_target_aligned_acpc as target_aligned
from tools.paper1_target_aligned_acpc import (
    candidate_response_metrics,
    fit_action_coordinate_stats,
    inverse_eval_action_coordinates,
    permute_candidate_actions,
    permute_candidate_time,
    planner_pool_costs,
    planner_query_info,
    planner_temporal_semantics,
    prediction_error_drift_certificate,
    replay_action_pool,
    replay_pusht_action_pool,
    replay_tworoom_action_pool,
    unpack_candidate_action_blocks,
)


class _CurrentOnlyCostModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.anchor = torch.nn.Parameter(torch.zeros(()), requires_grad=False)
        self.observation_steps: int | None = None

    def get_cost(
        self,
        info: dict[str, torch.Tensor],
        candidates: torch.Tensor,
    ) -> torch.Tensor:
        self.observation_steps = int(info["pixels"].size(2))
        assert info["pixels"].shape[:2] == candidates.shape[:2]
        assert info["goal"].shape[:2] == candidates.shape[:2]
        return candidates.square().sum(dim=(-1, -2))


def test_eval_planner_semantics_are_one_current_frame_and_five_predictions() -> None:
    semantics = planner_temporal_semantics(
        observation_steps=1,
        candidate_steps=5,
        action_block=5,
    )

    assert semantics.observation_steps == 1
    assert semantics.predicted_steps == 5
    assert semantics.low_level_action_steps == 25

    offline_mismatch = planner_temporal_semantics(
        observation_steps=3,
        candidate_steps=5,
        action_block=5,
    )
    assert offline_mismatch.predicted_steps == 3


def test_planner_query_selects_one_current_frame_and_separate_goal() -> None:
    pixels = torch.arange(2 * 7 * 3, dtype=torch.float32).reshape(2, 7, 3)
    actions = torch.arange(2 * 7 * 4, dtype=torch.float32).reshape(2, 7, 4)

    info = planner_query_info(
        {"pixels": pixels, "action": actions},
        current_index=2,
        goal_index=6,
    )

    assert info["pixels"].shape == (2, 1, 3)
    assert info["action"].shape == (2, 1, 4)
    assert info["goal"].shape == (2, 1, 3)
    assert torch.equal(info["pixels"][:, 0], pixels[:, 2])
    assert torch.equal(info["goal"][:, 0], pixels[:, 6])


def test_shared_pool_costs_never_reinterpret_candidate_as_history() -> None:
    model = _CurrentOnlyCostModel()
    batch = {
        "pixels": torch.randn(3, 8, 3, 4, 4),
        "action": torch.randn(3, 8, 10),
    }
    candidates = torch.randn(3, 6, 5, 10)

    costs = planner_pool_costs(
        model,
        batch,
        candidates,
        current_index=2,
        goal_index=7,
        device="cpu",
    )

    assert costs.shape == (3, 6)
    assert model.observation_steps == 1


def test_candidate_action_unpack_matches_policy_reshape_order() -> None:
    candidates = torch.arange(2 * 3 * 2 * 6).reshape(2, 3, 2, 6)

    unpacked = unpack_candidate_action_blocks(
        candidates,
        action_block=3,
        base_action_dim=2,
    )
    expected = candidates.reshape(2, 3, 6, 2)

    assert torch.equal(unpacked, expected)
    assert unpacked[0, 0].tolist() == [
        [0, 1],
        [2, 3],
        [4, 5],
        [6, 7],
        [8, 9],
        [10, 11],
    ]


def test_eval_action_inverse_matches_sklearn_standard_scaler() -> None:
    raw = np.array(
        [
            [-1.0, 2.0],
            [0.0, 4.0],
            [2.0, 8.0],
            [3.0, 16.0],
        ],
        dtype=np.float64,
    )
    normalized = np.array(
        [[-1.25, 0.5], [0.0, 0.0], [1.5, -0.75]],
        dtype=np.float64,
    )
    stats = fit_action_coordinate_stats(raw)
    scaler = StandardScaler().fit(raw)

    actual = inverse_eval_action_coordinates(normalized, stats)
    expected = scaler.inverse_transform(normalized)

    assert np.allclose(actual, expected, rtol=0.0, atol=1e-12)
    assert np.allclose(stats.mean, scaler.mean_[None], rtol=0.0, atol=1e-12)
    assert np.allclose(
        stats.eval_population_std,
        scaler.scale_[None],
        rtol=0.0,
        atol=1e-12,
    )
    assert not np.allclose(
        stats.training_sample_std,
        stats.eval_population_std,
        rtol=0.0,
        atol=1e-12,
    )


def test_tworoom_same_state_replay_is_deterministic_and_block_aligned() -> None:
    initial = np.array([[60.0, 60.0]], dtype=np.float32)
    goals = np.array([[180.0, 60.0]], dtype=np.float32)
    actions = np.zeros((1, 2, 10, 2), dtype=np.float32)
    actions[0, 1, :, 0] = 1.0

    first = replay_tworoom_action_pool(
        initial,
        goals,
        actions,
        action_block=5,
        reset_seed=11,
    )
    second = replay_tworoom_action_pool(
        initial,
        goals,
        actions,
        action_block=5,
        reset_seed=11,
    )

    assert first["block_states"].shape == (1, 2, 2, 2)
    assert np.array_equal(first["block_states"], second["block_states"])
    assert np.array_equal(first["endpoints"][0, 0], initial[0])
    assert first["endpoints"][0, 1, 0] > initial[0, 0]
    assert first["goal_distances"][0, 1] < first["goal_distances"][0, 0]


def test_pusht_same_state_replay_is_deterministic_and_dispatched() -> None:
    initial = np.array(
        [[100.0, 100.0, 250.0, 250.0, 0.0, 0.0, 0.0]],
        dtype=np.float64,
    )
    goals = np.array(
        [[300.0, 100.0, 250.0, 250.0, 0.0, 0.0, 0.0]],
        dtype=np.float64,
    )
    actions = np.zeros((1, 2, 4, 2), dtype=np.float64)
    actions[0, 1, :, 0] = 0.5

    first = replay_pusht_action_pool(
        initial,
        goals,
        actions,
        action_block=2,
        reset_seed=11,
    )
    second = replay_action_pool(
        "PushT",
        initial,
        goals,
        actions,
        action_block=2,
        reset_seed=11,
    )

    assert first["block_states"].shape == (1, 2, 2, 7)
    assert np.array_equal(first["block_states"], second["block_states"])
    assert np.array_equal(first["goal_distances"], second["goal_distances"])
    assert first["endpoints"][0, 1, 0] > first["endpoints"][0, 0, 0]


@pytest.mark.parametrize(
    ("task", "adapter_name"),
    [
        ("Reacher", "replay_reacher_action_pool"),
        ("Cube", "replay_cube_action_pool"),
    ],
)
def test_mujoco_tasks_use_the_same_replay_dispatch_contract(
    monkeypatch: pytest.MonkeyPatch,
    task: str,
    adapter_name: str,
) -> None:
    sentinel = {"task": task}

    def fake_adapter(*args, **kwargs):
        assert kwargs["action_block"] == 5
        assert kwargs["reset_seed"] == 7
        assert kwargs["return_pixels"] is True
        return sentinel

    monkeypatch.setattr(target_aligned, adapter_name, fake_adapter)
    output = target_aligned.replay_action_pool(
        task,
        np.zeros((1, 1)),
        np.zeros((1, 1)),
        np.zeros((1, 1, 5, 1)),
        action_block=5,
        reset_seed=7,
        return_pixels=True,
    )

    assert output is sentinel


def test_candidate_response_preserves_within_history_action_variation() -> None:
    nominal = torch.zeros(1, 3, 2, 2)
    probe = nominal.clone()
    probe[0, 0, 0, 0] = 1.0
    probe[0, 1, :, 0] = 2.0
    probe[0, 2, :, :] = 3.0

    metrics = candidate_response_metrics(
        nominal,
        probe,
        encoder_response=torch.tensor([2.0]),
    )

    assert metrics["candidate_h1_response"].shape == (1, 3)
    assert metrics["candidate_h1_response"][0].tolist() == pytest.approx(
        [1.0, 2.0, np.sqrt(18.0)]
    )
    assert torch.unique(metrics["candidate_horizon_response"]).numel() == 3
    assert torch.allclose(
        metrics["candidate_horizon_amplification"],
        metrics["candidate_horizon_response"] / 2.0,
    )


def test_correct_action_response_certifies_prediction_error_drift() -> None:
    nominal = torch.tensor(
        [[[[0.0, 0.0], [1.0, 0.0]], [[2.0, 0.0], [2.0, 1.0]]]]
    )
    probe = torch.tensor(
        [[[[1.0, 0.0], [3.0, 0.0]], [[2.0, 2.0], [4.0, 1.0]]]]
    )
    target = torch.tensor(
        [[[[0.5, 0.0], [0.0, 0.0]], [[1.0, 1.0], [3.0, 3.0]]]]
    )

    audit = prediction_error_drift_certificate(nominal, probe, target)

    assert torch.all(audit["h1_certificate_slack"] >= -1e-7)
    assert torch.all(audit["horizon_certificate_slack"] >= -1e-7)
    assert torch.allclose(
        audit["adverse_horizon_error_change"],
        audit["signed_horizon_error_change"].clamp_min(0.0),
    )


def test_mismatched_action_response_is_not_a_correct_action_certificate() -> None:
    target = torch.zeros(1, 1, 2, 1)
    correct_nominal = torch.zeros_like(target)
    correct_probe = torch.tensor([[[[0.0], [2.0]]]])
    wrong_action_nominal = torch.ones_like(target)
    wrong_action_probe = wrong_action_nominal.clone()

    correct = prediction_error_drift_certificate(
        correct_nominal, correct_probe, target
    )
    wrong_action_response = candidate_response_metrics(
        wrong_action_nominal, wrong_action_probe
    )["candidate_horizon_response"]

    assert correct["absolute_horizon_error_drift"].item() > 0.0
    assert wrong_action_response.item() == 0.0
    assert (
        wrong_action_response
        < correct["absolute_horizon_error_drift"]
    ).item()


def test_h1_response_cannot_certify_full_horizon_error_drift() -> None:
    target = torch.zeros(1, 1, 2, 1)
    nominal = torch.zeros_like(target)
    probe = torch.tensor([[[[0.0], [2.0]]]])

    audit = prediction_error_drift_certificate(nominal, probe, target)

    assert audit["h1_response"].item() == 0.0
    assert audit["absolute_horizon_error_drift"].item() > 0.0
    assert audit["horizon_certificate_slack"].item() >= -1e-7


def test_action_and_time_controls_preserve_marginals_but_break_alignment() -> None:
    candidates = torch.arange(2 * 4 * 5 * 3).reshape(2, 4, 5, 3)

    action_shuffled, action_permutation = permute_candidate_actions(
        candidates,
        seed=13,
    )
    time_shuffled, time_permutation = permute_candidate_time(
        candidates,
        seed=17,
    )

    assert action_permutation.shape == (2, 4)
    assert time_permutation.shape == (2, 4, 5)
    assert torch.equal(
        torch.sort(action_shuffled.flatten(1), dim=1).values,
        torch.sort(candidates.flatten(1), dim=1).values,
    )
    assert torch.equal(
        torch.sort(time_shuffled.flatten(2), dim=2).values,
        torch.sort(candidates.flatten(2), dim=2).values,
    )
    assert not torch.equal(action_shuffled, candidates)
    assert not torch.equal(time_shuffled, candidates)


@pytest.mark.parametrize(
    ("observed", "candidates"),
    [(0, 5), (3, 2)],
)
def test_invalid_planner_temporal_semantics_are_rejected(
    observed: int,
    candidates: int,
) -> None:
    with pytest.raises(ValueError):
        planner_temporal_semantics(
            observation_steps=observed,
            candidate_steps=candidates,
            action_block=5,
        )
