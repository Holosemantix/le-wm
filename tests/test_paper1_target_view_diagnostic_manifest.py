from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from tools import paper1_target_view_diagnostic_manifest as target_manifest


def _metric_text(seed: int, successes: int, *, reported_rate: float | None = None) -> str:
    episodes = [1] * successes + [0] * (100 - successes)
    rate = float(successes) if reported_rate is None else reported_rate
    return (
        f"seed: {seed}\n"
        "eval:\n"
        "  num_eval: 100\n"
        "corruption:\n"
        "  type: gaussian_noise\n"
        "  apply_to: [pixels]\n"
        "==== RESULTS ====\n"
        f"metrics: {{'success_rate': {rate}, "
        f"'episode_successes': array({episodes!r}), 'seeds': None}}\n"
    )


def _write_config(path: Path, *, rho: str, branch: str) -> None:
    target_line = "    target_view: origin\n" if branch == "target_view" else ""
    noise_type = "gaussian_noise" if branch == "target_view" else "gaussian"
    path.write_text(
        "seed: 3072\n"
        "image_noise:\n"
        f"  type: {noise_type}\n"
        "  std_min: 0.0\n"
        f"  std_max: {rho}\n"
        "  noise_prob: 1\n"
        "  apply_to_val: false\n"
        "loss:\n"
        "  pred:\n"
        "    space: raw\n"
        f"{target_line}"
        "wm:\n"
        "  history_size: 3\n"
        "max_epochs: 10\n",
        encoding="utf-8",
    )


def _rate(task_index: int, rho_index: int, branch: str, seed_index: int, metric_index: int) -> int:
    branch_offset = 0 if branch == "full_sequence" else -10
    return 60 + task_index + rho_index + branch_offset + seed_index - metric_index


def _make_complete_tree(tmp_path: Path) -> tuple[Path, Path, dict[tuple[str, str, str, int], int]]:
    data_root = tmp_path / "data"
    live_rates: dict[tuple[str, str, str, int], int] = {}
    legacy: dict[str, object] = {}
    conditions = list(target_manifest.EVAL_CONDITIONS.items())

    for task_index, (task, (task_root, prefix)) in enumerate(target_manifest.TASK_LAYOUT.items()):
        legacy[task] = {}
        for rho_index, rho in enumerate(target_manifest.RHO_KEYS):
            legacy_metrics = {}
            for branch in target_manifest.BRANCHES:
                subdir = target_manifest._run_name(prefix, rho, branch)
                run_dir = data_root / task_root / "ckpt" / subdir
                eval_dir = run_dir / "eval_results"
                eval_dir.mkdir(parents=True)
                _write_config(run_dir / "config.yaml", rho=rho, branch=branch)
                (run_dir / "model_epoch_10_object.ckpt").write_bytes(
                    f"{task}/{rho}/{branch}".encode()
                )
                metric_values: dict[str, list[float]] = {}
                for metric_index, (metric_name, source_condition) in enumerate(conditions):
                    metric_values[metric_name] = []
                    for seed_index, eval_seed in enumerate(target_manifest.EVAL_SEEDS):
                        successes = _rate(
                            task_index, rho_index, branch, seed_index, metric_index
                        )
                        live_rates[(task, rho, metric_name, eval_seed)] = successes
                        metric_values[metric_name].append(float(successes))
                        path = eval_dir / f"{source_condition}_seed{eval_seed}_metrics.txt"
                        path.write_text(
                            _metric_text(eval_seed, successes), encoding="utf-8"
                        )
                if branch == "full_sequence":
                    for metric_name, values in metric_values.items():
                        legacy_metrics[metric_name] = {
                            "mean": sum(values) / len(values),
                            "std": 0.0,
                            "n": 3,
                            "values": values,
                        }
            legacy[task][rho] = {"metrics": legacy_metrics}

    # A stale archive with a conflicting value must never be selected.
    archive = (
        data_root
        / "lewm-pusht"
        / "ckpt"
        / target_manifest._run_name("pusht", "0.08", "target_view")
        / "eval_results_old_code_history1_bug_20260606"
    )
    archive.mkdir()
    (archive / "origin_seed42_metrics.txt").write_text(
        _metric_text(42, 99), encoding="utf-8"
    )

    # Reproduce the known old-manifest/live disagreement while retaining live
    # eval_results as the sole behavior authority.
    stale_metric = legacy["PushT"]["0.08"]["metrics"]["pixels_std0.08"]
    stale_metric["values"] = [87.0, 85.0, 95.0]
    stale_metric["mean"] = 89.0

    legacy["_metadata"] = {"training_seed": 3072}
    legacy_path = tmp_path / "legacy.json"
    legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
    return data_root, legacy_path, live_rates


@pytest.fixture()
def complete_tree(tmp_path: Path):
    return _make_complete_tree(tmp_path)


def test_builds_complete_provenance_bound_matrix_and_prefers_live_eval(complete_tree):
    data_root, legacy_path, live_rates = complete_tree
    payload = target_manifest.build_manifest(
        data_root,
        legacy_manifest=legacy_path,
        code_commit="test-commit",
        created_utc="2026-07-10T00:00:00+00:00",
    )

    metadata = payload["_metadata"]
    assert metadata["status"] == "ok"
    assert metadata["actual_rows"] == 64
    assert metadata["actual_matched_pairs"] == 32
    assert len(payload["rows"]) == 64
    assert len(payload["matched_pairs"]) == 32
    assert metadata["old_history1_archive_glob"] == "eval_results_old_code_history1_bug*"
    assert len(metadata["old_history1_archives_excluded"]) == 1

    target_row = next(
        row
        for row in payload["rows"]
        if row["task"] == "PushT"
        and row["std_key"] == "0.08"
        and row["branch"] == "target_view"
    )
    assert target_row["config"]["validated"]["target_view_effective"] == "origin"
    assert target_row["metrics"]["clean"]["values"][0] == live_rates[
        ("PushT", "0.08", "clean", 42)
    ]
    assert target_row["metrics"]["clean"]["values"][0] != 99.0

    full_row = next(
        row
        for row in payload["rows"]
        if row["task"] == "PushT"
        and row["std_key"] == "0.08"
        and row["branch"] == "full_sequence"
    )
    assert full_row["config"]["validated"]["target_view_explicit"] is False
    assert full_row["config"]["validated"]["target_view_effective"] == "perturbed"
    assert full_row["metrics"]["pixels_std0.08"]["values"] != [87.0, 85.0, 95.0]

    conflicts = [
        conflict
        for conflict in payload["legacy_live_conflicts"]
        if conflict["task"] == "PushT"
        and conflict["std_key"] == "0.08"
        and conflict.get("metric") == "pixels_std0.08"
    ]
    assert conflicts == [
        {
            "kind": "legacy_live_value_mismatch",
            "task": "PushT",
            "std_key": "0.08",
            "metric": "pixels_std0.08",
            "legacy_values": [87.0, 85.0, 95.0],
            "legacy_mean": 89.0,
            "live_values": full_row["metrics"]["pixels_std0.08"]["values"],
            "live_mean": full_row["metrics"]["pixels_std0.08"]["mean"],
            "authority": "live_eval_results",
        }
    ]

    config_path = Path(target_row["config"]["path"])
    checkpoint_path = Path(target_row["checkpoint"]["path"])
    assert target_row["config"]["sha256"] == hashlib.sha256(
        config_path.read_bytes()
    ).hexdigest()
    assert target_row["checkpoint"]["sha256"] == hashlib.sha256(
        checkpoint_path.read_bytes()
    ).hexdigest()
    assert all(
        len(source_file["sha256"]) == 64
        for metric in target_row["metrics"].values()
        for source_file in metric["source_files"]
    )
    assert set(payload["runner_manifests"]) == set(target_manifest.BRANCHES)
    assert set(payload["runner_manifests"]["target_view"]["Cube"]) == set(
        target_manifest.RHO_KEYS
    )


def test_missing_live_eval_fails_closed(complete_tree):
    data_root, legacy_path, _ = complete_tree
    missing = (
        data_root
        / "lewm-cube"
        / "ckpt"
        / target_manifest._run_name("cube", "0.04", "target_view")
        / "eval_results"
        / "pixels_std0.05_seed43_metrics.txt"
    )
    missing.unlink()
    with pytest.raises(target_manifest.ManifestValidationError, match="missing live eval metric"):
        target_manifest.build_manifest(data_root, legacy_manifest=legacy_path)


def test_ambiguous_epoch10_object_checkpoint_fails_closed(complete_tree):
    data_root, legacy_path, _ = complete_tree
    run_dir = (
        data_root
        / "lewm-tworooms"
        / "ckpt"
        / target_manifest._run_name("tworoom", "0.01", "full_sequence")
    )
    (run_dir / "backup_epoch_10_object.ckpt").write_bytes(b"ambiguous")
    with pytest.raises(target_manifest.ManifestValidationError, match="exactly one epoch-10"):
        target_manifest.build_manifest(data_root, legacy_manifest=legacy_path)


def test_wrong_target_view_config_fails_closed(complete_tree):
    data_root, legacy_path, _ = complete_tree
    config = (
        data_root
        / "lewm-reacher"
        / "ckpt"
        / target_manifest._run_name("reacher", "0.05", "target_view")
        / "config.yaml"
    )
    config.write_text(
        config.read_text(encoding="utf-8").replace("target_view: origin", "target_view: perturbed"),
        encoding="utf-8",
    )
    with pytest.raises(target_manifest.ManifestValidationError, match="target_view=origin"):
        target_manifest.build_manifest(data_root, legacy_manifest=legacy_path)


def test_training_seed_and_std_are_validated(complete_tree):
    data_root, legacy_path, _ = complete_tree
    config = (
        data_root
        / "lewm-pusht"
        / "ckpt"
        / target_manifest._run_name("pusht", "0.02", "full_sequence")
        / "config.yaml"
    )
    config.write_text(
        config.read_text(encoding="utf-8").replace("seed: 3072", "seed: 3073"),
        encoding="utf-8",
    )
    with pytest.raises(target_manifest.ManifestValidationError, match="training seed 3072"):
        target_manifest.build_manifest(data_root, legacy_manifest=legacy_path)


def test_metric_episode_count_and_reported_rate_must_agree(complete_tree):
    data_root, legacy_path, _ = complete_tree
    metric = (
        data_root
        / "lewm-tworooms"
        / "ckpt"
        / target_manifest._run_name("tworoom", "0.01", "target_view")
        / "eval_results"
        / "origin_seed42_metrics.txt"
    )
    metric.write_text(_metric_text(42, 10, reported_rate=11.0), encoding="utf-8")
    with pytest.raises(target_manifest.ManifestValidationError, match="disagrees"):
        target_manifest.build_manifest(data_root, legacy_manifest=legacy_path)


def test_internal_duplicate_rows_are_rejected(complete_tree):
    data_root, legacy_path, _ = complete_tree
    payload = target_manifest.build_manifest(
        data_root, legacy_manifest=legacy_path, code_commit="test-commit"
    )
    duplicate = copy.deepcopy(payload)
    duplicate["rows"][-1]["row_id"] = duplicate["rows"][0]["row_id"]
    with pytest.raises(target_manifest.ManifestValidationError, match="duplicate row_id"):
        target_manifest._validate_complete_artifact(duplicate)


def test_cli_writes_blocked_report_and_returns_nonzero(tmp_path: Path):
    out = tmp_path / "blocked.json"
    return_code = target_manifest.main(
        [
            "--data-root",
            str(tmp_path / "missing-data"),
            "--out",
            str(out),
            "--no-legacy-compare",
        ]
    )
    assert return_code == 2
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["_metadata"]["status"] == "blocked"
    assert payload["rows"] == []
    assert payload["_metadata"]["errors"]
