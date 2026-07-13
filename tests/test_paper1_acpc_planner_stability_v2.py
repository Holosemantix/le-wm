from __future__ import annotations

import pytest
import torch

from tools.paper1_acpc_planner_stability_audit import (
    tie_aware_decision_metrics as v1_tie_aware_decision_metrics,
)
from tools.paper1_acpc_planner_stability_audit_v2 import (
    tie_aware_decision_metrics as v2_tie_aware_decision_metrics,
)


def test_v2_avoids_float32_signed_gap_cancellation() -> None:
    generator = torch.Generator().manual_seed(0)
    nominal = torch.randn(512, 64, generator=generator) * 10_000.0
    probe = torch.randn(512, 64, generator=generator) * 10_000.0

    with pytest.raises(RuntimeError, match="signed perturbed-gap identity mismatch"):
        v1_tie_aware_decision_metrics(nominal, probe, invariant_atol=1e-5)

    metrics = v2_tie_aware_decision_metrics(
        nominal,
        probe,
        invariant_atol=1e-5,
    )
    winner = metrics["nominal_winner"].unsqueeze(1)
    direct_gap = probe.double() - probe.double().gather(1, winner)
    competitor_gap = direct_gap.clone()
    competitor_gap.scatter_(1, winner, float("inf"))

    assert torch.equal(
        metrics["exact_stable"],
        torch.argmin(nominal, dim=1) == torch.argmin(probe, dim=1),
    )
    assert torch.allclose(
        metrics["min_signed_probe_gap"],
        competitor_gap.min(dim=1).values,
        rtol=0.0,
        atol=1e-12,
    )
