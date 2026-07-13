from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "paper1/config/paired_multiseverity_protocol_v1.json"
HASH_PATH = ROOT / "paper1/config/paired_multiseverity_protocol_v1.sha256"
EXPECTED_PROTOCOL_SHA256 = "6712b4f595444d751d9c327262c288e37dbd80be7ddde9bb4fd336ed41119622"
ADDENDUM_PATH = ROOT / "paper1/config/paired_multiseverity_execution_addendum_v1.json"
ADDENDUM_HASH_PATH = ROOT / "paper1/config/paired_multiseverity_execution_addendum_v1.sha256"
ADDENDUM_V2_PATH = ROOT / "paper1/config/paired_multiseverity_execution_addendum_v2.json"
ADDENDUM_V2_HASH_PATH = ROOT / "paper1/config/paired_multiseverity_execution_addendum_v2.sha256"
EXPECTED_ADDENDUM_V2_SHA256 = "ac89c6c69ae67e123c90205a9de532f9a0bb9709ad91c5404c1f43dc23ea5afb"
EXPECTED_ADDENDUM_SHA256 = "70ca8cb9a361f144ca047235ae5844e0859394dd350cb021eb8c5720845d44c2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _protocol() -> dict:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def test_protocol_hash_sidecar_freezes_pre_execution_contract() -> None:
    sidecar_hash, sidecar_path = HASH_PATH.read_text(encoding="utf-8").split()
    assert sidecar_path == "paper1/config/paired_multiseverity_protocol_v1.json"
    assert sidecar_hash == EXPECTED_PROTOCOL_SHA256
    assert _sha256(PROTOCOL_PATH) == EXPECTED_PROTOCOL_SHA256


def test_protocol_preregisters_complete_primary_grid_and_zero_rule() -> None:
    protocol = _protocol()
    scope = protocol["scope"]
    analysis = protocol["primary_analysis"]
    diagnostic = protocol["diagnostic"]
    execution = protocol["execution"]

    assert protocol["status"] == "frozen_pre_execution"
    assert scope["primary_model_family"] == "LeWM"
    assert scope["training_seeds"] == [3072, 3073, 3074]
    assert scope["tasks"] == ["TwoRoom", "PushT", "Reacher", "Cube"]
    assert protocol["stressors"]["gaussian_blur"]["primary_nonidentity"] == [7, 11, 15]
    assert protocol["stressors"]["resize"]["primary_nonidentity"] == [0.75, 0.5, 0.25]
    assert analysis["expected_pairs"] == (
        len(scope["training_seeds"])
        * len(scope["tasks"])
        * len(protocol["stressors"])
        * 3
    )
    assert analysis["expected_pairs"] == 72
    assert analysis["block_count"] == 12
    assert analysis["exact_randomization"] == (
        "enumerate all 2^12 task-x-training-seed block sign flips"
    )
    assert diagnostic["paired_rule"].endswith("greater than zero")
    assert diagnostic["decision_threshold"] == 0
    assert diagnostic["threshold_search_allowed"] is False
    assert diagnostic["severity_search_allowed"] is False
    assert execution["max_concurrent_eval_jobs"] == 1
    assert execution["max_concurrent_diagnostic_jobs"] == 1


def test_protocol_binds_every_measurement_source_by_hash() -> None:
    protocol = _protocol()
    assert protocol["source_paths"].keys() == protocol["source_hashes"].keys()
    for name, relative_path in protocol["source_paths"].items():
        assert _sha256(ROOT / relative_path) == protocol["source_hashes"][name]


def test_runners_are_serial_resumable_and_watchdog_bounded() -> None:
    behavior = (ROOT / "paper1/scripts/run_paired_multiseverity_behavior.sh").read_text(
        encoding="utf-8"
    )
    atr = (ROOT / "paper1/scripts/run_paired_multiseverity_atr.sh").read_text(
        encoding="utf-8"
    )

    for token in (
        "plan|smoke|full",
        "--only-missing",
        'eval_max_concurrency=1',
        'eval_resume=1',
        'eval_save_video=0',
        'eval_timeout_seconds=',
        "timeout --signal=TERM --kill-after=60s",
        "frozen protocol hash mismatch",
    ):
        assert token in behavior
    for token in (
        "valid_shard",
        "status_counts",
        "timeout --signal=TERM --kill-after=60s",
        "PAPER1_DIAGNOSTIC_THREADS",
        "frozen protocol hash mismatch",
    ):
        assert token in atr

def test_execution_addendum_is_transparent_and_hash_bound() -> None:
    sidecar_hash, sidecar_path = ADDENDUM_HASH_PATH.read_text(
        encoding="utf-8"
    ).split()
    assert sidecar_path == (
        "paper1/config/paired_multiseverity_execution_addendum_v1.json"
    )
    assert sidecar_hash == EXPECTED_ADDENDUM_SHA256
    assert _sha256(ADDENDUM_PATH) == EXPECTED_ADDENDUM_SHA256

    addendum = json.loads(ADDENDUM_PATH.read_text(encoding="utf-8"))
    disclosure = addendum["non_blind_disclosure"]
    assert addendum["parent_protocol"]["sha256"] == EXPECTED_PROTOCOL_SHA256
    assert disclosure["created_after_behavior_and_atr_smoke"] is True
    assert disclosure["behavior_outcomes_were_inspected_before_this_addendum"] is True
    assert disclosure["analysis_threshold_or_severity_changed"] is False
    assert addendum["pre_smpr_revision"][
        "reference_or_smpr_output_created_before_fix"
    ] is False
    for entry in addendum["execution_only_sources"].values():
        assert _sha256(ROOT / entry["path"]) == entry["sha256"]
    for entry in addendum["bound_measurement_sources"].values():
        assert _sha256(ROOT / entry["path"]) == entry["sha256"]


def test_smpr_smoke_matches_atr_and_remains_claim_ineligible() -> None:
    smpr_path = (
        ROOT
        / "paper1/results/multiseverity_v1/raw/lewm_seed3072"
        / "gaussian_blur_ks7/smpr_tworoom_v2.json"
    )
    payload = json.loads(smpr_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["status"] == "complete"
    assert payload["metadata"]["status_counts"] == {"ok": 2}
    assert len(payload["rows"]) == 2
    assert all(row["atr_reference_match"] is True for row in payload["rows"])
    assert all(row["atr_reference_abs_error"] == 0 for row in payload["rows"])

    by_std = {row["std_key"]: row for row in payload["rows"]}
    assert by_std["0.0"]["smpr"] == 0.016393441706895828
    assert by_std["0.08"]["smpr"] == 0.9672130346298218

    runner = (ROOT / "paper1/scripts/run_paired_multiseverity_smpr.sh").read_text(
        encoding="utf-8"
    )
    for token in (
        "valid_reference",
        "valid_smpr",
        "atr_reference_match == true",
        "for training_seed in 3072 3073 3074",
        "timeout --signal=TERM --kill-after=60s",
        'verify_frozen_file "$addendum"',
    ):
        assert token in runner

def test_multiseverity_exact_block_test_and_dose_response_use_all_six_rows() -> None:
    sys.path.insert(0, str(ROOT))
    from paper1.scripts.build_paired_multiseverity_summary import (
        _blocks,
        _dose_response,
        _exact_randomization,
    )

    rows = []
    tasks = ("TwoRoom", "PushT", "Reacher", "Cube")
    seeds = (3072, 3073, 3074)
    severity_order = {
        "blur": (7.0, 11.0, 15.0),
        "resize": (0.75, 0.5, 0.25),
    }
    for block_index, (task, seed) in enumerate(
        (task, seed) for task in tasks for seed in seeds
    ):
        for family_index, (family, severities) in enumerate(severity_order.items()):
            for rank, severity in enumerate(severities, start=1):
                value = float(block_index * 10 + family_index * 3 + rank)
                rows.append(
                    {
                        "task": task,
                        "training_seed_or_family_id": f"lewm_seed{seed}",
                        "stressor_family": family,
                        "stressor_severity": severity,
                        "severity_key": f"{family}:{severity:g}",
                        "delta_behavior": value,
                        "delta_joint_score": value,
                    }
                )

    assert len(rows) == 72
    assert len(_blocks(rows)) == 12
    exact = _exact_randomization(rows)
    assert exact["rows_retained_per_block"] == 6
    assert exact["enumerated_assignments"] == 4096
    assert abs(exact["observed_spearman"] - 1.0) < 1e-12
    assert exact["one_sided_p_value"] == 1 / 4096
    assert exact["row_level_signed_agreement"]["successes"] == 72

    dose = _dose_response(rows)
    assert dose["curve_count"] == 24
    assert dose["no_monotonicity_filtering"] is True
    assert dose["behavior_nondecreasing_fraction"] == 1.0
    assert dose["joint_nondecreasing_fraction"] == 1.0

def test_v2_addendum_task_binds_references_and_retains_v1_failures() -> None:
    sidecar_hash, sidecar_path = ADDENDUM_V2_HASH_PATH.read_text(
        encoding="utf-8"
    ).split()
    assert sidecar_path == (
        "paper1/config/paired_multiseverity_execution_addendum_v2.json"
    )
    assert sidecar_hash == EXPECTED_ADDENDUM_V2_SHA256
    assert _sha256(ADDENDUM_V2_PATH) == EXPECTED_ADDENDUM_V2_SHA256

    addendum = json.loads(ADDENDUM_V2_PATH.read_text(encoding="utf-8"))
    assert addendum["parent_protocol"]["sha256"] == EXPECTED_PROTOCOL_SHA256
    assert addendum["parent_execution_addendum"]["sha256"] == (
        EXPECTED_ADDENDUM_SHA256
    )
    failure = addendum["failure_disclosure"]
    assert failure["reference_binding_failed"] is True
    assert failure["threshold_or_severity_changed"] is False
    assert failure["v1_outputs_before_failure"] == {
        "valid_tworoom_shards": 4,
        "unmatched_pusht_shards": 1,
        "remaining_unattempted_shards": 43,
    }
    for section in ("execution_sources", "bound_measurement_sources"):
        for entry in addendum[section].values():
            assert _sha256(ROOT / entry["path"]) == entry["sha256"]

    current = (
        ROOT
        / "paper1/results/multiseverity_v1/raw/lewm_seed3072"
        / "gaussian_blur_ks7/smpr_tworoom_v2.json"
    )
    payload = json.loads(current.read_text(encoding="utf-8"))
    assert payload["metadata"]["source_paths"]["reference_atr"].endswith(
        "acpc_tworoom_horizon_v2_checkpoint_bound.json"
    )
    assert all(row["atr_reference_match"] is True for row in payload["rows"])

    directory = current.parent
    archived_tworoom = list(
        directory.glob("smpr_tworoom_v2.json.pre_v2_or_invalid_*")
    )
    archived_pusht = list(
        directory.glob("smpr_pusht_v2.json.pre_v2_or_invalid_*")
    )
    assert len(archived_tworoom) == 1
    assert len(archived_pusht) == 1
    assert _sha256(archived_tworoom[0]) == (
        "73da06004db247d38d5330b51bc55d348529c836547065dc334010b791ca5bc3"
    )
    assert _sha256(archived_pusht[0]) == (
        "a15b7292d5b7c15d293729bfdd7c1eabf6e2c516153e07289079fca3ba5f4762"
    )

    runner = (
        ROOT / "paper1/scripts/run_paired_multiseverity_smpr_v2.sh"
    ).read_text(encoding="utf-8")
    for token in (
        "valid_reference",
        'acpc_${task_slug}_horizon_v2_checkpoint_bound.json',
        ".metadata.task == $task",
        ".metadata.source_sha256 == $raw_sha",
        ".metadata.source_hashes.reference_atr == $reference_sha",
        ".atr_reference_match == true",
    ):
        assert token in runner
