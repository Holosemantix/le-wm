from pathlib import Path
import sys

import pytest
import torch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from paper1.scripts.smpr_controls import (
    _oracle_value,
    _quartile_labels,
    _select_pairs,
)


def test_quartile_labels_cover_ordered_cells():
    feature = torch.arange(8, dtype=torch.float32).unsqueeze(1)
    labels = _quartile_labels(feature)

    assert labels.min().item() == 0
    assert labels.max().item() == 3
    assert torch.unique(labels).numel() == 4


def test_cross_same_and_far_pair_controls_are_distinct():
    state = torch.tensor([[0.0], [0.1], [0.2], [1.0]])
    labels = torch.tensor([0, 0, 1, 1])
    cross = _select_pairs(
        state=state,
        labels=labels,
        local_quantile=1.0,
        mode="cross_label",
    )
    same = _select_pairs(
        state=state,
        labels=labels,
        local_quantile=1.0,
        mode="same_label",
    )
    far = _select_pairs(
        state=state,
        labels=None,
        local_quantile=1.0,
        mode="far",
    )

    assert cross["pair_count"] == same["pair_count"] == far["pair_count"] == 4
    assert not torch.equal(cross["pair_neighbor_indices"], same["pair_neighbor_indices"])
    assert torch.equal(far["pair_neighbor_indices"], torch.tensor([3, 3, 3, 0]))


def test_tworoom_oracle_routes_cross_wall_pairs_through_door():
    state = torch.tensor([[100.0, 100.0], [100.0, 100.0]])
    target = torch.tensor([[105.0, 100.0], [120.0, 100.0]])
    values, rule, delta = _oracle_value(
        task="TwoRoom",
        state_raw=state,
        target_raw=target,
    )

    assert values[1] > values[0]
    assert "door" in rule
    assert delta == pytest.approx(0.10)


def test_pusht_oracle_includes_pose_and_pusher_object_distance():
    state = torch.tensor([[0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0]])
    goal = torch.tensor([[0.0, 0.0, 20.0, 0.0, 0.0, 0.0, 0.0]])
    values, rule, _ = _oracle_value(
        task="PushT",
        state_raw=state,
        target_raw=goal,
    )

    assert values.item() > 0.0
    assert "pusher-object" in rule
