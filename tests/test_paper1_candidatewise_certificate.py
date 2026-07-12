from pathlib import Path
import sys

import pytest
import torch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.paper1_sample_level_certificate import (
    _certificate_for_pool,
    _wilson_lower_one_sided95,
)
from paper1.scripts.fixed_pool_certificate_calibration import _block_bootstrap


def test_sharp_certificate_uses_candidatewise_winner_and_competitor_drifts():
    clean = torch.tensor([[0.0, 10.0, 20.0]])
    noisy = torch.tensor([[1.0, 9.0, 19.0]])

    result = _certificate_for_pool(clean, noisy)

    assert result["sharp_slack"].item() == pytest.approx(8.0)
    assert result["sharp_pass"].item() is True
    assert result["flips"].item() is False


def test_observed_flip_is_contained_in_sharp_certificate_failure():
    clean = torch.tensor([[0.0, 1.0]])
    noisy = torch.tensor([[2.0, 0.0]])

    result = _certificate_for_pool(clean, noisy)

    assert result["sharp_slack"].item() < 0.0
    assert result["sharp_pass"].item() is False
    assert result["flips"].item() is True


def test_sharp_certificate_invariant_holds_over_random_cost_tables():
    generator = torch.Generator().manual_seed(17)
    clean = torch.randn((128, 65), generator=generator)
    noisy = clean + 0.1 * torch.randn((128, 65), generator=generator)

    result = _certificate_for_pool(clean, noisy)

    assert not bool(result["flips"][result["sharp_pass"]].any())


def test_one_sided_wilson_lower_bound_is_nontrivial_and_bounded():
    lower = _wilson_lower_one_sided95(80, 100)

    assert 0.0 < lower < 0.8
    assert _wilson_lower_one_sided95(0, 100) == pytest.approx(0.0)


def test_block_bootstrap_is_deterministic_and_bounded():
    blocks = [
        {
            "n": 100,
            "coarse_pass": 25,
            "sharp_pass": 60,
            "flip": 20,
            "sharp_fail": 40,
            "flip_when_sharp_fail": 20,
        },
        {
            "n": 100,
            "coarse_pass": 50,
            "sharp_pass": 80,
            "flip": 10,
            "sharp_fail": 20,
            "flip_when_sharp_fail": 10,
        },
    ]

    first = _block_bootstrap(blocks, repetitions=50, seed=17)
    second = _block_bootstrap(blocks, repetitions=50, seed=17)

    assert first == second
    for interval in first["metrics"].values():
        assert 0.0 <= interval["lower"] <= interval["upper"] <= 1.0
