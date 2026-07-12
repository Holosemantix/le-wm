#!/usr/bin/env python3
"""Score canonical PLDM E2 only after frozen blind predictions exist."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from paper1.scripts.frozen_external_validation import (
    BLIND_FIELDS,
    ROOT,
    TASKS,
    RHO_GRID,
    _as_bool,
    _auprc,
    _confusion,
    _finite,
    _joint_values,
    _load_strict,
    _protocol,
    _read_csv,
    _sha256,
    _write_csv_exclusive,
    _write_json_exclusive,
    _assert_protocol_unchanged,
)
from tools.build_canonical_evals_pldm import _parse_success_rate


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _manifest_behavior(
    *,
    manifest_path: Path,
    protocol: Mapping[str, Any],
) -> tuple[
    dict[tuple[int, str, float], dict[str, Any]],
    dict[str, str],
    dict[str, str],
    str,
    int,
]:
    manifest = _load_strict(manifest_path)
    metadata = manifest.get("_metadata", {})
    _require(
        metadata.get("schema_version")
        == "paper1-pldm-canonical-eval-manifest-0.2",
        "PLDM behavior manifest schema mismatch",
    )
    _require(metadata.get("status") == "complete", "PLDM behavior manifest incomplete")
    _require(metadata.get("model_family") == "PLDM", "PLDM behavior family mismatch")
    _require(metadata.get("tasks") == list(TASKS), "PLDM behavior task coverage mismatch")
    _require(
        tuple(metadata.get("std_keys", [])) == tuple(str(rho) for rho in RHO_GRID),
        "PLDM behavior rho coverage mismatch",
    )
    evaluation_seeds = [
        int(seed)
        for seed in protocol["behavior_evaluation"]["evaluation_seeds"]
    ]
    _require(
        metadata.get("evaluation_seeds") == evaluation_seeds,
        "PLDM behavior evaluation seeds mismatch",
    )
    family_id = str(metadata["training_family_id"])
    training_seed = int(metadata["training_seed"])
    _require(
        family_id == f"pldm_canonical_seed{training_seed}",
        "PLDM behavior family id/seed mismatch",
    )

    source_paths: dict[str, str] = {"pldm_manifest": str(manifest_path)}
    source_hashes: dict[str, str] = {"pldm_manifest": _sha256(manifest_path)}
    metric_values: dict[tuple[str, float, str], list[float]] = {}
    for task in TASKS:
        _require(set(manifest[task]) == {str(rho) for rho in RHO_GRID}, f"{task}: rho coverage mismatch")
        for rho in RHO_GRID:
            std_key = str(rho)
            entry = manifest[task][std_key]
            run_path = Path(str(entry["path"]))
            _require(run_path.is_dir(), f"missing PLDM run path: {run_path}")
            for metric_name in ("clean", "pixels_std0.08"):
                metric = entry.get("metrics", {}).get(metric_name, {})
                _require(metric.get("seeds") == evaluation_seeds, f"{task}/{rho}: eval seeds mismatch")
                _require(int(metric.get("n", -1)) == len(evaluation_seeds), f"{task}/{rho}: metric n mismatch")
                recorded_values = [
                    _finite(value, name=f"{task}/{rho}/{metric_name}/manifest")
                    for value in metric.get("values", [])
                ]
                _require(len(recorded_values) == len(evaluation_seeds), f"{task}/{rho}: value coverage mismatch")
                live_values: list[float] = []
                for index, evaluation_seed in enumerate(evaluation_seeds):
                    metric_path = (
                        run_path
                        / "eval_results"
                        / f"{metric_name}_seed{evaluation_seed}_metrics.txt"
                    )
                    _require(metric_path.is_file(), f"missing PLDM metric source: {metric_path}")
                    value = _parse_success_rate(metric_path)
                    _require(
                        math.isclose(
                            value,
                            recorded_values[index],
                            rel_tol=0.0,
                            abs_tol=1e-6,
                        ),
                        f"{task}/{rho}/{metric_name}/seed{evaluation_seed}: value mismatch",
                    )
                    live_values.append(value)
                    rho_key = f"{rho:.2f}".replace(".", "p")
                    source_key = (
                        f"behavior_{task}_{rho_key}_{metric_name}_seed{evaluation_seed}"
                    )
                    source_paths[source_key] = str(metric_path)
                    source_hashes[source_key] = _sha256(metric_path)
                _require(
                    math.isclose(
                        sum(live_values) / len(live_values),
                        _finite(metric.get("mean"), name=f"{task}/{rho}/{metric_name}/mean"),
                        rel_tol=0.0,
                        abs_tol=1e-6,
                    ),
                    f"{task}/{rho}/{metric_name}: mean mismatch",
                )
                metric_values[(task, rho, metric_name)] = live_values

    recovery_fraction = float(protocol["gaussian_behavior_label"]["recovery_fraction"])
    clean_tolerance = float(protocol["gaussian_behavior_label"]["clean_tolerance_pp"])
    behavior: dict[tuple[int, str, float], dict[str, Any]] = {}
    for task in TASKS:
        base_clean = sum(metric_values[(task, 0.0, "clean")]) / len(evaluation_seeds)
        base_stress = sum(metric_values[(task, 0.0, "pixels_std0.08")]) / len(evaluation_seeds)
        stress_means = {
            rho: sum(metric_values[(task, rho, "pixels_std0.08")])
            / len(evaluation_seeds)
            for rho in RHO_GRID
        }
        best_stress = max(stress_means.values())
        recovery_threshold = base_stress + recovery_fraction * (
            best_stress - base_stress
        )
        denominator = max(best_stress - base_stress, 1e-12)
        for rho in RHO_GRID:
            clean_values = metric_values[(task, rho, "clean")]
            stress_values = metric_values[(task, rho, "pixels_std0.08")]
            clean = sum(clean_values) / len(clean_values)
            stress = sum(stress_values) / len(stress_values)
            clean_pass = clean >= base_clean - clean_tolerance
            label = stress >= recovery_threshold and clean_pass
            behavior[(training_seed, task, rho)] = {
                "clean_score": clean,
                "stress_score": stress,
                "clean_score_by_evaluation_seed": clean_values,
                "stress_score_by_evaluation_seed": stress_values,
                "base_clean_score": base_clean,
                "base_stress_score": base_stress,
                "best_stress_score": best_stress,
                "recovery_score_threshold": recovery_threshold,
                "normalized_recovery": (stress - base_stress) / denominator,
                "clean_constraint_pass": clean_pass,
                "behavior_label": label,
            }
    _require(set(source_paths) == set(source_hashes), "PLDM behavior provenance keys differ")
    return behavior, source_paths, source_hashes, family_id, training_seed


def score_pldm(
    *,
    protocol_path: Path,
    predictions_path: Path,
    manifest_path: Path,
    out_rows_path: Path,
    out_summary_path: Path,
    out_blocks_path: Path,
    created_utc: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    protocol, protocol_sha, original, mtime_ns = _protocol(protocol_path)
    for output in (out_rows_path, out_summary_path, out_blocks_path):
        if output.resolve() == protocol_path.resolve():
            raise ValueError("PLDM score output cannot be the protocol path")
        if output.exists():
            raise FileExistsError(output)
    blind = _read_csv(predictions_path)
    _require(len(blind) == len(TASKS) * len(RHO_GRID), "PLDM blind row count mismatch")
    _require(set(blind[0]) == set(BLIND_FIELDS), "PLDM blind field schema mismatch")
    _require(
        all(row.get("protocol_sha256") == protocol_sha for row in blind),
        "PLDM blind protocol hash mismatch",
    )
    sidecar_path = Path(str(predictions_path) + ".metadata.json")
    sidecar = _load_strict(sidecar_path)
    sidecar_metadata = sidecar.get("metadata", {})
    _require(sidecar_metadata.get("protocol_hash") == protocol_sha, "PLDM sidecar protocol mismatch")
    _require(sidecar_metadata.get("behavior_blind") is True, "PLDM predictions are not blind")
    apply_script = ROOT / "paper1" / "scripts" / "frozen_external_validation.py"
    _require(
        sidecar_metadata.get("script_sha256") == _sha256(apply_script),
        "PLDM blind producer hash differs from frozen apply",
    )
    sidecar_paths = sidecar_metadata.get("source_paths", {})
    sidecar_hashes = sidecar_metadata.get("source_hashes", {})
    _require(set(sidecar_paths) == set(sidecar_hashes), "PLDM sidecar provenance keys differ")
    _require(sidecar.get("row_count") == len(blind), "PLDM sidecar row count mismatch")
    _require(sidecar.get("fields") == list(BLIND_FIELDS), "PLDM sidecar field schema mismatch")
    _require(sidecar_hashes.get("protocol") == protocol_sha, "PLDM sidecar source protocol mismatch")
    _require(
        sidecar_hashes.get("blind_rows") == _sha256(predictions_path),
        "PLDM blind rows hash mismatch",
    )
    diagnostics_path = Path(str(sidecar_paths["diagnostics"]))
    if not diagnostics_path.is_absolute():
        diagnostics_path = ROOT / diagnostics_path
    _require(
        diagnostics_path.is_file()
        and _sha256(diagnostics_path) == sidecar_hashes.get("diagnostics"),
        "PLDM diagnostic source hash mismatch",
    )
    tau_atr = _finite(protocol["tau_atr"], name="tau_atr")
    tau_smpr = _finite(protocol["tau_smpr"], name="tau_smpr")
    for row in blind:
        expected = _joint_values(
            atr=_finite(row["atr_horizon_v2_q90"], name="PLDM ATR"),
            smpr=_finite(row["smpr"], name="PLDM SMPR"),
            tau_atr=tau_atr,
            tau_smpr=tau_smpr,
        )
        for field, value in zip(
            ("atr_threshold_margin", "smpr_threshold_margin", "joint_score"),
            expected[:3],
        ):
            _require(
                math.isclose(
                    _finite(row[field], name=f"PLDM {field}"),
                    value,
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ),
                f"PLDM blind {field} mismatch",
            )
        _require(
            _as_bool(row["frozen_gate_pass"]) is expected[3],
            "PLDM blind gate mismatch",
        )

    behavior, behavior_paths, behavior_hashes, family_id, training_seed = (
        _manifest_behavior(manifest_path=manifest_path, protocol=protocol)
    )
    blind_index: dict[tuple[int, str, float], dict[str, str]] = {}
    for row in blind:
        _require(row.get("model_family") == "PLDM", "PLDM score rejects another family")
        _require(row.get("training_family_id") == family_id, "PLDM family id mismatch")
        seed = int(float(row["training_seed"]))
        _require(seed == training_seed, "PLDM training seed mismatch")
        _require(row.get("split_name") == "E2", "PLDM score rejects non-E2 row")
        _require(row.get("stressor_family") == "gaussian", "PLDM stressor mismatch")
        _require(
            math.isclose(
                float(row["stressor_severity"]),
                float(protocol["diagnostic_sampling"]["evaluation_noise_std"]),
                rel_tol=0.0,
                abs_tol=1e-12,
            ),
            "PLDM stressor severity mismatch",
        )
        key = (seed, str(row["task"]), float(row["training_rho"]))
        _require(key not in blind_index, f"duplicate PLDM blind row {key}")
        blind_index[key] = row
    _require(set(blind_index) == set(behavior), "PLDM blind/behavior coverage mismatch")

    scored: list[dict[str, Any]] = []
    for key in sorted(behavior, key=lambda value: (TASKS.index(value[1]), value[2])):
        seed, task, rho = key
        pred = blind_index[key]
        truth = behavior[key]
        scored.append(
            {
                "model_family": "PLDM",
                "training_family_id": family_id,
                "training_seed": seed,
                "task": task,
                "training_rho": rho,
                "stressor_family": pred["stressor_family"],
                "stressor_severity": float(pred["stressor_severity"]),
                "atr_horizon_v2_q90": float(pred["atr_horizon_v2_q90"]),
                "smpr": float(pred["smpr"]),
                "joint_score": float(pred["joint_score"]),
                "frozen_gate_pass": pred["frozen_gate_pass"],
                **{
                    name: (
                        json.dumps(value, separators=(",", ":"))
                        if isinstance(value, list)
                        else _bool_text(value)
                        if isinstance(value, bool)
                        else value
                    )
                    for name, value in truth.items()
                },
                "split_name": "E2",
                "protocol_sha256": protocol_sha,
                "diagnostics_sha256": pred["diagnostics_sha256"],
            }
        )
    y_true = [_as_bool(row["behavior_label"]) for row in scored]
    y_pred = [_as_bool(row["frozen_gate_pass"]) for row in scored]
    joint_scores = [float(row["joint_score"]) for row in scored]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        grouped[str(row["task"])].append(row)
    blocks: list[dict[str, Any]] = []
    for task in TASKS:
        block = sorted(grouped[task], key=lambda row: float(row["training_rho"]))
        true_rhos = [
            float(row["training_rho"])
            for row in block
            if _as_bool(row["behavior_label"])
        ]
        pred_rhos = [
            float(row["training_rho"])
            for row in block
            if _as_bool(row["frozen_gate_pass"])
        ]
        true_onset = min(true_rhos) if true_rhos else None
        pred_onset = min(pred_rhos) if pred_rhos else None
        if true_onset is None and pred_onset is None:
            onset_error = 0.0
        elif true_onset is None:
            onset_error = -1.0
        elif pred_onset is None:
            onset_error = 1.0
        else:
            onset_error = pred_onset - true_onset
        block_truth = [_as_bool(row["behavior_label"]) for row in block]
        block_pred = [_as_bool(row["frozen_gate_pass"]) for row in block]
        blocks.append(
            {
                "model_family": "PLDM",
                "training_family_id": family_id,
                "training_seed": training_seed,
                "task": task,
                "behavioral_onset": true_onset,
                "predicted_onset": pred_onset,
                "onset_error": onset_error,
                "false_early": sum(
                    1
                    for row in block
                    if _as_bool(row["frozen_gate_pass"])
                    and true_onset is not None
                    and float(row["training_rho"]) < true_onset
                ),
                "false_late": sum(
                    1
                    for row in block
                    if _as_bool(row["behavior_label"])
                    and not _as_bool(row["frozen_gate_pass"])
                ),
                **_confusion(block_truth, block_pred),
                "protocol_sha256": protocol_sha,
            }
        )
    confusion = _confusion(y_true, y_pred)
    metrics = {
        **confusion,
        "auprc": _auprc(y_true, joint_scores),
        "mean_absolute_onset_error": sum(abs(float(row["onset_error"])) for row in blocks)
        / len(blocks),
        "max_absolute_onset_error": max(abs(float(row["onset_error"])) for row in blocks),
        "false_early": sum(int(row["false_early"]) for row in blocks),
        "false_late": sum(int(row["false_late"]) for row in blocks),
    }
    script_path = Path(__file__).resolve()
    parse_script = ROOT / "tools" / "build_canonical_evals_pldm.py"
    source_paths = {
        "protocol": str(protocol_path),
        "predictions": str(predictions_path),
        "predictions_sidecar": str(sidecar_path),
        "diagnostics": str(diagnostics_path),
        **behavior_paths,
    }
    source_hashes = {
        "protocol": protocol_sha,
        "predictions": _sha256(predictions_path),
        "predictions_sidecar": _sha256(sidecar_path),
        "diagnostics": _sha256(diagnostics_path),
        **behavior_hashes,
    }
    _require(set(source_paths) == set(source_hashes), "PLDM summary provenance keys differ")
    summary = {
        "metadata": {
            "schema_version": "paper1-pldm-frozen-external-validation-summary-1.1",
            "created_utc": created_utc or datetime.now(timezone.utc).isoformat(),
            "code_commit": protocol["code_commit"],
            "script_path": str(script_path.relative_to(ROOT)),
            "script_sha256": _sha256(script_path),
            "behavior_parser_path": str(parse_script.relative_to(ROOT)),
            "behavior_parser_sha256": _sha256(parse_script),
            "source_paths": source_paths,
            "source_hashes": source_hashes,
            "protocol_hash": protocol_sha,
            "model_family": "PLDM",
            "training_family_id": family_id,
            "training_seeds": [training_seed],
            "training_seed_semantics": "one independently trained PLDM checkpoint family",
            "evaluation_seeds": [
                int(seed)
                for seed in protocol["behavior_evaluation"]["evaluation_seeds"]
            ],
            "evaluation_seed_semantics": "conditional evaluation variability, not training-run replication",
            "status": "complete",
            "status_counts": {"ok": len(scored)},
            "missing_rows": [],
            "errors": [],
            "threshold_search_available": False,
            "strict_external_contract": sidecar_metadata.get(
                "strict_external_contract"
            ),
            "operator_blinding": sidecar_metadata.get("operator_blinding"),
            "behavior_join_after_blind_predictions": True,
            "auprc_definition": (
                "tie-aware stepwise Average Precision; exact joint_score ties "
                "enter each retrieval set together"
            ),
        },
        "metrics": metrics,
        "raw_confusion": {key: confusion[key] for key in ("tp", "tn", "fp", "fn")},
        "blocks": blocks,
    }
    _write_csv_exclusive(out_rows_path, scored)
    _write_csv_exclusive(out_blocks_path, blocks)
    _write_json_exclusive(out_summary_path, summary)
    _assert_protocol_unchanged(protocol_path, original=original, mtime_ns=mtime_ns)
    return scored, summary, blocks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-rows", type=Path, required=True)
    parser.add_argument("--out-summary", type=Path, required=True)
    parser.add_argument("--out-blocks", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rows, summary, blocks = score_pldm(
        protocol_path=args.protocol,
        predictions_path=args.predictions,
        manifest_path=args.manifest,
        out_rows_path=args.out_rows,
        out_summary_path=args.out_summary,
        out_blocks_path=args.out_blocks,
    )
    print(f"wrote {args.out_rows} ({len(rows)} scored rows)")
    print(f"wrote {args.out_blocks} ({len(blocks)} task blocks)")
    print(f"wrote {args.out_summary} (AUPRC={summary['metrics']['auprc']:.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
