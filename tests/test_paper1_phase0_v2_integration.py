from __future__ import annotations

from typing import Any

import pytest
import torch
import torch.nn.functional as F

from tools import paper1_phase0_acpc as phase0
from tools.paper1_acpc_metrics import (
    compute_acpc_horizon_metrics,
    horizon_weighted_stacked_l2,
    per_anchor_clean_transition_scale,
)


def _shift_stats(clean: torch.Tensor, noisy: torch.Tensor) -> dict[str, float]:
    clean = clean.reshape(-1, clean.shape[-1])
    noisy = noisy.reshape(-1, noisy.shape[-1])
    l2 = torch.linalg.vector_norm(noisy - clean, dim=-1)
    cosine = 1.0 - F.cosine_similarity(clean, noisy, dim=-1)
    return {
        "l2_median": float(torch.quantile(l2, 0.50)),
        "l2_p90": float(torch.quantile(l2, 0.90)),
        "cos_dist_median": float(torch.quantile(cosine, 0.50)),
    }


def _rollout(
    _model: Any,
    init: torch.Tensor,
    _act_emb: torch.Tensor,
    _history_size: int,
    n_steps: int,
) -> torch.Tensor:
    predictions = init[:, -1:].expand(-1, n_steps, -1)
    return torch.cat((init, predictions), dim=1)


def _assert_no_tensors(value: Any) -> None:
    assert not torch.is_tensor(value)
    if isinstance(value, dict):
        for child in value.values():
            _assert_no_tensors(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _assert_no_tensors(child)


def test_prediction_metrics_aggregate_draws_per_anchor_before_q90(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(phase0, "torch", torch)
    monkeypatch.setattr(phase0, "get_embedding_space", lambda outputs, _space: outputs["emb"])
    monkeypatch.setattr(phase0, "_shift_stats", _shift_stats)
    monkeypatch.setattr(
        phase0,
        "_clean_nn_dist",
        lambda _value: {"l2": 1.0, "cos": 1.0},
    )
    monkeypatch.setattr(
        phase0,
        "_open_loop_target_shift",
        lambda _model, clean, noisy, _actions, _history: {
            "clean_pred": clean[:, :1],
            "noisy_pred": noisy[:, :1],
        },
    )
    monkeypatch.setattr(phase0, "_autoregressive_rollout", _rollout)
    monkeypatch.setattr(
        phase0, "compute_acpc_horizon_metrics", compute_acpc_horizon_metrics
    )
    monkeypatch.setattr(
        phase0, "horizon_weighted_stacked_l2", horizon_weighted_stacked_l2
    )
    monkeypatch.setattr(
        phase0,
        "per_anchor_clean_transition_scale",
        per_anchor_clean_transition_scale,
    )

    clean_emb = torch.tensor(
        [
            [[0.0], [1.0], [2.0]],
            [[0.0], [1.0], [2.0]],
        ],
        dtype=torch.float64,
    )
    act_emb = torch.zeros((2, 2, 1), dtype=torch.float64)
    clean_outputs = {"emb": clean_emb, "act_emb": act_emb}

    noisy_draws = []
    for markers in ([1.0, 5.0], [3.0, 7.0]):
        noisy_emb = clean_emb.clone()
        noisy_emb[:, 0, 0] = torch.tensor(markers, dtype=torch.float64)
        noisy_draws.append({"emb": noisy_emb, "act_emb": act_emb})

    result = phase0.compute_acpc_prediction_metrics(
        object(),
        clean_outputs,
        noisy_draws,
        history_size=1,
        rollout_horizon=2,
        embedding_space="normalized",
        eps=1e-12,
    )

    assert result["radius_metric"] == "horizon_weighted_stacked_l2_v2"
    assert result["noise_draw_aggregation"] == (
        "per_anchor_mean_then_checkpoint_quantile"
    )
    torch.testing.assert_close(
        torch.tensor(result["horizon_radius_per_noise_draw"], dtype=torch.float64),
        torch.tensor([[1.0, 3.0], [5.0, 7.0]], dtype=torch.float64),
        rtol=0.0,
        atol=1e-10,
    )
    torch.testing.assert_close(
        torch.tensor(result["horizon_radius_per_anchor"], dtype=torch.float64),
        torch.tensor([2.0, 6.0], dtype=torch.float64),
        rtol=0.0,
        atol=1e-10,
    )
    assert result["atr_horizon_v2_q90"] == pytest.approx(5.6)
    assert result["stepwise_rollout_q90"] == result["acpc_h_l2_p90_legacy"]
    assert result["stepwise_rollout_q90_is_atr"] is False
    assert "acpc_h_l2_p90" not in result
    _assert_no_tensors(result)


def test_draw_metric_aggregation_and_parser_defaults() -> None:
    aggregated = phase0._mean_numeric_draw_metrics(
        [
            {"score": 1.0, "candidate_count": 65.0, "rule": "shared"},
            {"score": 3.0, "candidate_count": 65.0, "rule": "shared"},
        ]
    )
    assert aggregated == {
        "score": 2.0,
        "candidate_count": 65.0,
        "rule": "shared",
    }

    args = phase0.build_parser().parse_args([])
    assert args.num_noise_draws == 1
    assert args.out.endswith("_v2.json")
    with pytest.raises(SystemExit):
        phase0.build_parser().parse_args(["--num-noise-draws", "0"])
