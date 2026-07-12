from pathlib import Path
import sys

import pytest
import torch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.paper1_acpc_metrics import uniform_horizon_weights, weighted_stacked_rollout
from tools.paper1_jvp_hutchinson_sensitivity_audit import (
    SCHEMA_VERSION,
    _jsonable,
    _normal_mean_ci95,
    build_parser,
    kappa_relative_isotropic,
    kappa_submultiplicative,
    write_table,
)
from paper1.scripts.plot_gaussian_sensitivity_mechanism import (
    _kappa_relative_isotropic_vs_base as plot_kappa_relative_vs_base,
)


def _exact_kappas(j_g: torch.Tensor, j_e: torch.Tensor) -> tuple[float, float]:
    composed_sq = float((j_g @ j_e).square().sum())
    rollout_sq = float(j_g.square().sum())
    encoder_sq = float(j_e.square().sum())
    kappa_sub = kappa_submultiplicative(
        composed_frobenius_sq=composed_sq,
        rollout_frobenius_sq=rollout_sq,
        encoder_frobenius_sq=encoder_sq,
        eps=0.0,
    )
    return kappa_sub, kappa_relative_isotropic(
        kappa_sub,
        latent_input_dim=j_e.shape[0],
    )


def test_exact_linear_map_kappas_match_matrix_norms():
    j_e = torch.tensor(
        [[1.0, 2.0], [0.0, -1.0], [3.0, 0.5]],
        dtype=torch.float64,
    )
    j_g = torch.tensor(
        [[2.0, -1.0, 0.0], [0.5, 1.5, -2.0]],
        dtype=torch.float64,
    )

    kappa_sub, kappa_relative = _exact_kappas(j_g, j_e)
    expected_sub = float(
        (j_g @ j_e).square().sum()
        / (j_g.square().sum() * j_e.square().sum())
    )

    assert kappa_sub == pytest.approx(expected_sub, rel=1e-12, abs=1e-12)
    assert kappa_sub <= 1.0 + 1e-12
    assert kappa_relative == pytest.approx(j_e.shape[0] * kappa_sub)


def test_relative_isotropic_gain_uses_full_batched_latent_dimension():
    latent_feature_dim = 3
    j_e = torch.diag(torch.tensor([1.0, 0.0, 0.0], dtype=torch.float64))
    j_g = torch.tensor([[1.0, 0.0, 0.0]], dtype=torch.float64)
    single_sub, single_relative = _exact_kappas(j_g, j_e)

    batch_size = 4
    batched_j_e = torch.block_diag(*([j_e] * batch_size))
    batched_j_g = torch.block_diag(*([j_g] * batch_size))
    batch_sub, batch_relative = _exact_kappas(batched_j_g, batched_j_e)

    assert single_sub == pytest.approx(1.0)
    assert single_relative == pytest.approx(float(latent_feature_dim))
    assert single_relative > 1.0
    assert batch_sub == pytest.approx(single_sub / batch_size)
    assert batched_j_e.shape[0] == batch_size * latent_feature_dim
    assert batch_relative == pytest.approx(single_relative)
    assert batch_relative == pytest.approx(batched_j_e.shape[0] * batch_sub)


def test_finite_probe_kappa_estimate_is_not_clipped():
    kappa_sub = kappa_submultiplicative(
        composed_frobenius_sq=1.25,
        rollout_frobenius_sq=1.0,
        encoder_frobenius_sq=1.0,
        eps=0.0,
    )

    assert kappa_sub == pytest.approx(1.25)
    assert kappa_relative_isotropic(kappa_sub, latent_input_dim=3) == pytest.approx(3.75)


def test_finite_probe_interval_is_reported_without_clipping():
    interval = _normal_mean_ci95([0.0, 2.0])

    assert interval is not None
    assert interval[0] < 0.0
    assert interval[1] > 0.0


def test_weighted_stacked_vectorization_matches_canonical_sqrt_alpha_map():
    rollout = torch.arange(12, dtype=torch.float64).reshape(2, 3, 2)
    weights = uniform_horizon_weights(
        3,
        dtype=rollout.dtype,
        device=rollout.device,
    )

    stacked = weighted_stacked_rollout(rollout, weights=weights)
    expected = (rollout * weights.sqrt().reshape(1, 3, 1)).reshape(2, 6)

    assert stacked.shape == (2, 6)
    assert torch.allclose(stacked, expected)
    assert torch.allclose(
        stacked.square().sum(dim=-1),
        rollout.square().sum(dim=-1).mean(dim=-1),
    )


def test_weighted_stacked_vectorization_supports_forward_ad_jvp():
    rollout = torch.arange(12, dtype=torch.float64).reshape(2, 3, 2)
    tangent = torch.ones_like(rollout)
    weights = uniform_horizon_weights(3, dtype=rollout.dtype)

    _, jvp = torch.func.jvp(
        lambda value: weighted_stacked_rollout(value, weights=weights),
        (rollout,),
        (tangent,),
    )

    expected = weighted_stacked_rollout(tangent, weights=weights)
    torch.testing.assert_close(jvp, expected)


def test_jvp_v2_defaults_and_json_conversion_are_explicit():
    args = build_parser().parse_args([])

    assert SCHEMA_VERSION == "paper1-jvp-hutchinson-sensitivity-0.2"
    assert args.out_json.name.endswith("_v2.json")
    assert args.out_csv.name.endswith("_v2.csv")
    assert args.summary_csv.name.endswith("_v2.csv")
    assert _jsonable({"nan": float("nan"), "inf": float("inf")}) == {
        "nan": None,
        "inf": None,
    }


def test_jvp_table_prefers_canonical_kappa_key_and_describes_unbounded_ratio(tmp_path):
    out = tmp_path / "jvp_table.tex"
    write_table(
        out,
        [
            {
                "task": "TwoRoom",
                "checkpoint_type": "endpoint",
                "n_sequences": 4,
                "hutchinson_probes": 2,
                "encoder_trace_per_pixel_dim_vs_base": 0.1,
                "rollout_trace_per_latent_dim_vs_base": 0.2,
                "composed_trace_per_pixel_dim_vs_base": 0.3,
                "kappa_relative_isotropic_vs_base": 2.5,
                "alignment_coefficient_vs_base": 0.5,
            }
        ],
        "tab:test-jvp",
    )

    rendered = out.read_text(encoding="utf-8")
    assert r"\shortstack{raw encoder\\trace}" in rendered
    assert r"\shortstack{relative isotropic\\gain}" in rendered
    assert "relative isotropic alignment gain" in rendered
    assert "can exceed 1 and is not an angle" in rendered
    assert "2.500" in rendered
    assert "0.500" not in rendered


def test_plot_kappa_reader_prefers_new_key_and_supports_legacy_alias():
    assert plot_kappa_relative_vs_base(
        {
            "kappa_relative_isotropic_vs_base": "2.25",
            "alignment_coefficient_vs_base": "0.75",
        }
    ) == pytest.approx(2.25)
    assert plot_kappa_relative_vs_base(
        {"alignment_coefficient_vs_base": "0.75"}
    ) == pytest.approx(0.75)
