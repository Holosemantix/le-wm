from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools import paper1_unseen_eval_grid as grid


def _write_canonical(path: Path, entry: dict[str, object]) -> Path:
    path.write_text(json.dumps({"TwoRoom": {"0.08": entry}}), encoding="utf-8")
    return path


def _args(root: Path, canonical: Path):
    return grid.build_parser().parse_args(
        [
            "--root",
            str(root),
            "--canonical",
            str(canonical),
            "--tasks",
            "TwoRoom",
            "--std-keys",
            "0.08",
            "--families",
            "gaussian_blur",
            "--family-magnitudes",
            "gaussian_blur=15",
            "--dry-run",
        ]
    )


def _run_dir(root: Path, subdir: str = "tworoom_pldm_noise_0to008_p1") -> Path:
    path = root / "lewm-tworooms" / "ckpt" / subdir
    path.mkdir(parents=True)
    return path


def test_explicit_model_file_is_authoritative_and_persisted(tmp_path: Path) -> None:
    root = tmp_path / "data"
    run_dir = _run_dir(root)
    checkpoint = run_dir / "tworoom_pldm_noise_0to008_p1_20260522_epoch_10_object.ckpt"
    checkpoint.write_bytes(b"explicit canonical checkpoint")
    canonical = _write_canonical(
        tmp_path / "canonical.json",
        {
            "path": str(run_dir),
            "subdir": run_dir.name,
            "model_file": str(checkpoint),
            "metrics": {},
        },
    )

    manifest, jobs = grid.build_jobs(_args(root, canonical))

    assert manifest["metadata"]["schema_version"] == "paper1-unseen-eval-grid-manifest-1.1"
    assert len(jobs) == 1
    job = jobs[0]
    assert job["checkpoint_resolution"] == "canonical_model_file"
    assert job["checkpoint_exists"] is True
    assert job["checkpoint_rel"] == checkpoint.relative_to(root).as_posix()
    assert job["model_file"] == str(checkpoint.resolve())
    assert job["model_sha256"] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert f"ckpt_override=$DATA_ROOT/{job['checkpoint_rel']}" in job["command_template"]

    written = grid.write_manifest(manifest, tmp_path / "jobs.json")
    public_job = json.loads(written.read_text(encoding="utf-8"))["jobs"][0]
    assert public_job["model_file"] == str(checkpoint.resolve())
    assert public_job["model_sha256"] == job["model_sha256"]


def test_explicit_model_file_must_exist_and_never_falls_back(tmp_path: Path) -> None:
    root = tmp_path / "data"
    run_dir = _run_dir(root)
    fallback = run_dir / f"{run_dir.name}_epoch_10_object.ckpt"
    fallback.write_bytes(b"must not be selected")
    canonical = _write_canonical(
        tmp_path / "canonical.json",
        {
            "path": str(run_dir),
            "subdir": run_dir.name,
            "model_file": str(run_dir / "missing_epoch_10_object.ckpt"),
            "metrics": {},
        },
    )

    with pytest.raises(FileNotFoundError, match="canonical model_file does not exist"):
        grid.build_jobs(_args(root, canonical))


def test_explicit_model_file_must_be_within_entry_path(tmp_path: Path) -> None:
    root = tmp_path / "data"
    run_dir = _run_dir(root)
    outside = root / "outside_epoch_10_object.ckpt"
    outside.write_bytes(b"outside")
    canonical = _write_canonical(
        tmp_path / "canonical.json",
        {
            "path": str(run_dir),
            "subdir": run_dir.name,
            "model_file": str(outside),
            "metrics": {},
        },
    )

    with pytest.raises(ValueError, match="canonical model_file escapes entry path"):
        grid.build_jobs(_args(root, canonical))


def test_legacy_manifest_accepts_only_one_epoch_candidate(tmp_path: Path) -> None:
    root = tmp_path / "data"
    run_dir = _run_dir(root)
    unique = run_dir / "nonstandard_20260522_epoch_10_object.ckpt"
    unique.write_bytes(b"legacy unique")
    canonical = _write_canonical(
        tmp_path / "canonical.json",
        {"path": str(run_dir), "subdir": run_dir.name, "metrics": {}},
    )

    _, jobs = grid.build_jobs(_args(root, canonical))
    assert jobs[0]["model_file"] == str(unique.resolve())
    assert jobs[0]["checkpoint_resolution"] == "legacy_unique_epoch_match"

    (run_dir / "second_epoch_10_object.ckpt").write_bytes(b"ambiguous")
    with pytest.raises(ValueError, match="ambiguous legacy checkpoints"):
        grid.build_jobs(_args(root, canonical))


def test_eval_job_complete_requires_every_seed_metrics_artifact(
    tmp_path: Path,
) -> None:
    result_dir = tmp_path / "eval_results"
    result_dir.mkdir()
    (result_dir / "eval_summary.csv").write_text(
        "group,n_seeds,seeds,metric,mean,std,sem,values\n"
        'pixels_blur_ks15,3,"42,43,44",success_rate,1,0,0,"1;1;1"\n',
        encoding="utf-8",
    )
    labels = grid._expected_eval_labels(
        family="gaussian_blur",
        magnitudes=("15",),
        apply_to="1",
        eval_seeds=3,
        eval_base_seed=42,
    )
    assert labels == [
        "pixels_blur_ks15_seed42",
        "pixels_blur_ks15_seed43",
        "pixels_blur_ks15_seed44",
    ]

    for label in labels:
        (result_dir / f"{label}_metrics.txt").write_text(
            "==== RESULTS ====\nevaluation_time: 1 seconds\n",
            encoding="utf-8",
        )
    assert grid._eval_job_complete(
        result_dir=result_dir,
        family="gaussian_blur",
        magnitudes=("15",),
        apply_to="1",
        eval_seeds=3,
        eval_base_seed=42,
    )

    (result_dir / f"{labels[-1]}_metrics.txt").unlink()
    assert not grid._eval_job_complete(
        result_dir=result_dir,
        family="gaussian_blur",
        magnitudes=("15",),
        apply_to="1",
        eval_seeds=3,
        eval_base_seed=42,
    )
