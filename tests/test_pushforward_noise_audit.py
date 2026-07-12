from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
from torch import nn

from jepa import JEPA
from tools.acpc_flow.pushforward_noise_audit import (
    audit_pushforward_space,
    covariance_geometry,
    sample_diagonal_empirical,
    sample_isotropic_trace,
    sample_lowrank_diag_empirical,
    structured_family_samples,
)


class DummyEncoder(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.proj = nn.Linear(5, dim)

    def forward(self, pixels, interpolate_pos_encoding=True):
        cls = self.proj(pixels)
        return SimpleNamespace(last_hidden_state=cls.unsqueeze(1))


class DummyPredictor(nn.Module):
    def forward(self, x, c):
        return x + 0.1 * c[..., : x.size(-1)]


def build_dummy_jepa(dim=4):
    return JEPA(
        encoder=DummyEncoder(dim),
        predictor=DummyPredictor(),
        action_encoder=nn.Linear(2, dim),
        projector=nn.Identity(),
        pred_proj=nn.Identity(),
    )


def test_pushforward_covariance_geometry_detects_low_rank_direction():
    base = torch.linspace(-1.0, 1.0, 20)
    delta = torch.stack([base, 0.1 * base, torch.zeros_like(base)], dim=1)

    metrics = covariance_geometry(delta)

    assert metrics["cov_trace"] > 0
    assert metrics["top1_energy"] > 0.99
    assert metrics["cov_effective_rank"] < 1.2
    assert 0.0 <= metrics["diagonal_energy_ratio"] <= 1.0


def test_pushforward_structured_samplers_preserve_shapes():
    torch.manual_seed(0)
    delta = torch.randn(64, 6)
    delta[:, 0] *= 6.0

    iso = sample_isotropic_trace(delta, seed=1)
    diag = sample_diagonal_empirical(delta, seed=2)
    lr = sample_lowrank_diag_empirical(delta, rank=2, seed=3)
    samples = structured_family_samples(delta, ranks=[1, 2], mixture_delta=delta, seed=4)

    assert iso.shape == delta.shape
    assert diag.shape == delta.shape
    assert lr.shape == delta.shape
    assert set(samples) >= {"isotropic", "diagonal", "lowrank_r1", "lowrank_r2", "mixture", "pixel_paired"}
    assert torch.isfinite(iso).all()
    assert torch.isfinite(diag).all()
    assert torch.isfinite(lr).all()


def test_pushforward_audit_space_pure_smoke_with_dummy_model():
    torch.manual_seed(1)
    model = build_dummy_jepa(dim=4)
    clean = torch.randn(5, 3, 4)
    pixel_delta = torch.zeros_like(clean)
    pixel_delta[..., 0] = 0.2
    corrupt = clean + pixel_delta
    act_emb = torch.randn(5, 3, 4)
    state = torch.randn(5, 3, 2)

    metrics = audit_pushforward_space(
        model=model,
        level="emb",
        clean=clean,
        corrupt=corrupt,
        act_emb=act_emb,
        state=state,
        replay_context=None,
        ranks=[1, 2],
        replay_families=["diagonal"],
        mixture_delta=(corrupt - clean).reshape(-1, 4),
        reference_delta=(corrupt - clean).reshape(-1, 4),
        knn_k=2,
        seed=7,
        future_steps=3,
        history_size=3,
        topk=2,
        amplification={"amp_P_q90": 1.0},
    )

    assert "coverage_isotropic_q95" in metrics
    assert "coverage_lowrank_r1_q95" in metrics
    assert "synthetic_families" in metrics
    assert metrics["synthetic_families"]["pixel_paired"]["coverage_q95"] == 1.0
    assert metrics["decision"] in {
        "diagonal_candidate",
        "family_mixture_candidate",
        "isotropic_no_go",
        "lowrank_diag_candidate",
        "needs_semantic_guard",
        "no_go",
        "pixel_paired_upper_bound_only",
        "training_time_only",
    }
