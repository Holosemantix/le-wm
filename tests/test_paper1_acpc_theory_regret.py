from __future__ import annotations

import torch

from tools.paper1_acpc_planner_stability_audit import mse_cost_acpc_metrics


def test_mse_cost_bounds_control_fixed_pool_clean_regret() -> None:
    goal = torch.zeros(2, 2)
    nominal_z = torch.tensor(
        [
            [[0.0, 0.0], [0.8, 0.0], [1.2, 0.0]],
            [[0.1, 0.0], [0.4, 0.0], [1.0, 0.0]],
        ]
    )
    probe_z = torch.tensor(
        [
            [[0.9, 0.0], [0.2, 0.0], [1.2, 0.0]],
            [[0.2, 0.0], [0.35, 0.0], [0.9, 0.0]],
        ]
    )
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
    nominal_winner = nominal_costs.argmin(dim=1, keepdim=True)
    probe_winner = probe_costs.argmin(dim=1, keepdim=True)
    clean_regret = (
        nominal_costs.gather(1, probe_winner)
        - nominal_costs.gather(1, nominal_winner)
    )
    bound = result["mse_cost_drift_upper_bound"]
    regret_bound = bound.gather(1, probe_winner) + bound.gather(
        1, nominal_winner
    )

    assert bool((clean_regret >= 0.0).all())
    assert bool((clean_regret <= regret_bound + 1e-6).all())
    assert clean_regret[0].item() > 0.0
