from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper1.scripts.build_linearization_horizon_artifact import (
    summarize_horizons,
)
from tools.paper1_linearization_horizon_audit import (
    HORIZONS,
    QUANTILES,
    SMALL_SIGMAS,
    calibration_row_metrics,
    log_remainder_order,
)


def test_required_sensitivity_grids_are_explicit_and_frozen():
    assert SMALL_SIGMAS == (0.0025, 0.005, 0.01, 0.02)
    assert HORIZONS == (1, 2, 4, 8)
    assert QUANTILES == (0.80, 0.90, 0.95)


def test_exact_linear_measurement_has_unit_ratio_and_zero_error():
    row = calibration_row_metrics(
        measured_mean_r2=0.01**2 * 7.5,
        sigma=0.01,
        jvp_trace_per_sequence=7.5,
    )

    assert row["empirical_mean_R2_over_sigma2"] == pytest.approx(7.5)
    assert row["measured_to_jvp_ratio"] == pytest.approx(1.0)
    assert row["relative_error"] == pytest.approx(0.0)
    assert row["absolute_remainder"] == pytest.approx(0.0)


def test_log_remainder_order_recovers_cubic_growth():
    rows = [
        {"sigma": sigma, "absolute_remainder": 2.0 * sigma**3}
        for sigma in SMALL_SIGMAS
    ]

    assert log_remainder_order(rows) == pytest.approx(3.0, abs=1e-12)


def test_horizon_summary_uses_training_seed_medians_and_endpoint_base_ratio():
    rows = []
    tasks = ("TwoRoom", "PushT", "Reacher", "Cube")
    seeds = (3072, 3073, 3074)
    for task in tasks:
        for checkpoint_type, value in (("base", 2.0), ("onset", 1.0), ("endpoint", 0.5)):
            for seed in seeds:
                for horizon in HORIZONS:
                    for quantile in QUANTILES:
                        rows.append(
                            {
                                "task": task,
                                "checkpoint_type": checkpoint_type,
                                "training_seed": seed,
                                "horizon": horizon,
                                "ir_quantile": quantile,
                                "ir_horizon_v2": value + (seed - 3073) * 0.1,
                            }
                        )

    summary = summarize_horizons(rows)

    assert len(summary) == 4 * 4 * 3
    first = summary[0]
    assert first["base_ir_median"] == pytest.approx(2.0)
    assert first["endpoint_ir_median"] == pytest.approx(0.5)
    assert first["endpoint_to_base_ratio"] == pytest.approx(0.25)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"measured_mean_r2": -1.0, "sigma": 0.01, "jvp_trace_per_sequence": 1.0},
        {"measured_mean_r2": 1.0, "sigma": 0.0, "jvp_trace_per_sequence": 1.0},
        {"measured_mean_r2": 1.0, "sigma": 0.01, "jvp_trace_per_sequence": -1.0},
    ],
)
def test_calibration_metrics_reject_invalid_domains(kwargs):
    with pytest.raises(ValueError):
        calibration_row_metrics(**kwargs)
