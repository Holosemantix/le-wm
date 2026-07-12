from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from paper1.scripts.freeze_diagnostic_protocol import (
    ROOT,
    _load_strict,
    build_calibration_rows,
    build_parser,
    calibrate_global_gate,
    freeze,
)
from paper1.scripts.frozen_external_validation import (
    _heldout_behavior,
    _joint_values,
    apply_protocol,
    build_parser as build_external_parser,
)


ATR_PATH = ROOT / "assets" / "paper1_data" / "acpc_horizon_v2_lewm.json"
SMPR_PATH = (
    ROOT
    / "assets"
    / "paper1_data"
    / "smpr_calibration_lewm_seed3072_v2.json"
)
EVAL_PATH = (
    ROOT
    / "assets"
    / "paper1_data"
    / "training_seed_eval_manifests"
    / "lewm_seed3072_evals.json"
)
SCHEMA_PATH = (
    ROOT
    / "paper1"
    / "config"
    / "frozen_diagnostic_protocol_v1.schema.json"
)
PROTOCOL_PATH = (
    ROOT
    / "paper1"
    / "config"
    / "frozen_diagnostic_protocol_v1.json"
)


def _strict_load(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )


def _calibration_rows() -> list[dict]:
    return build_calibration_rows(
        atr_payload=_load_strict(ATR_PATH),
        smpr_payload=_load_strict(SMPR_PATH),
        eval_payload=_load_strict(EVAL_PATH),
    )


def test_calibration_rows_are_exactly_seed3072_cal() -> None:
    rows = _calibration_rows()

    assert len(rows) == 36
    assert {row["model_family"] for row in rows} == {"LeWM"}
    assert {row["training_seed"] for row in rows} == {3072}
    assert {row["split_name"] for row in rows} == {"CAL"}
    assert {
        (row["task"], row["training_rho"])
        for row in rows
    } == {
        (task, rho)
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for rho in (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08)
    }


def test_calibration_rejects_non_cal_training_seed() -> None:
    atr = copy.deepcopy(_load_strict(ATR_PATH))
    atr["metadata"]["training_seed"] = 3073

    with pytest.raises(ValueError, match="seed3072"):
        build_calibration_rows(
            atr_payload=atr,
            smpr_payload=_load_strict(SMPR_PATH),
            eval_payload=_load_strict(EVAL_PATH),
        )


def test_exact_metric_tie_prefers_stricter_atr_and_smpr_boundaries() -> None:
    selected, candidates = calibrate_global_gate(_calibration_rows())
    tied = [
        candidate
        for candidate in candidates
        if candidate["f1"] == selected["f1"]
        and candidate["precision"] == selected["precision"]
        and candidate["recall"] == selected["recall"]
        and candidate["predicted_positive"] == selected["predicted_positive"]
    ]

    assert selected["tau_atr"] == min(candidate["tau_atr"] for candidate in tied)
    same_atr = [
        candidate
        for candidate in tied
        if candidate["tau_atr"] == selected["tau_atr"]
    ]
    assert selected["tau_smpr"] == max(
        candidate["tau_smpr"] for candidate in same_atr
    )


def test_freeze_cli_has_no_external_or_threshold_override() -> None:
    parser = build_parser()
    destinations = {action.dest for action in parser._actions}

    assert {
        "calibration_atr",
        "calibration_smpr",
        "calibration_evals",
        "schema",
        "out",
        "audit_out",
    } <= destinations
    assert not {
        "external",
        "heldout",
        "pldm",
        "tau_atr",
        "tau_smpr",
        "threshold",
    } & destinations


def test_freeze_is_strict_schema_validated_and_exclusive(tmp_path: Path) -> None:
    protocol_path = tmp_path / "protocol.json"
    audit_path = tmp_path / "audit.json"
    protocol, _audit = freeze(
        calibration_atr_path=ATR_PATH,
        calibration_smpr_path=SMPR_PATH,
        calibration_evals_path=EVAL_PATH,
        schema_path=SCHEMA_PATH,
        out_path=protocol_path,
        audit_path=audit_path,
        frozen_at_utc="2026-07-10T00:00:00+00:00",
    )

    parsed = _strict_load(protocol_path)
    schema = _strict_load(SCHEMA_PATH)
    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(parsed)
    assert parsed == protocol
    assert parsed["immutable"] is True
    assert parsed["external_policy"]["threshold_search_allowed"] is False
    assert parsed["external_policy"]["protocol_write_allowed"] is False
    assert parsed["tau_atr"] > 0
    assert 0 <= parsed["tau_smpr"] <= 1
    assert parsed["calibration_audit_sha256"] == hashlib.sha256(
        audit_path.read_bytes()
    ).hexdigest()

    before_protocol = protocol_path.read_bytes()
    before_audit = audit_path.read_bytes()
    with pytest.raises(FileExistsError):
        freeze(
            calibration_atr_path=ATR_PATH,
            calibration_smpr_path=SMPR_PATH,
            calibration_evals_path=EVAL_PATH,
            schema_path=SCHEMA_PATH,
            out_path=protocol_path,
            audit_path=audit_path,
            frozen_at_utc="2026-07-10T00:00:00+00:00",
        )
    assert protocol_path.read_bytes() == before_protocol
    assert audit_path.read_bytes() == before_audit


def _diagnostic_input(
    path: Path,
    *,
    behavior_value: float = 1.0,
    protocol_hash: str | None = None,
) -> None:
    protocol_hash = protocol_hash or hashlib.sha256(
        PROTOCOL_PATH.read_bytes()
    ).hexdigest()
    protocol = _strict_load(PROTOCOL_PATH)
    payload = {
        "metadata": {
            "schema_version": "paper1-frozen-diagnostic-input-1.0",
            "protocol_sha256": protocol_hash,
            "training_seed_semantics": "synthetic external training family",
            "evaluation_seed_semantics": "not used by blind apply",
            "status": "complete",
            "missing_rows": [],
            "errors": [],
        },
        "rows": [
            {
                "status": "ok",
                "model_family": "LeWM",
                "training_family_id": "synthetic",
                "training_seed": 3073,
                "task": "TwoRoom",
                "training_rho": 0.01,
                "stressor_family": "gaussian",
                "stressor_severity": 0.08,
                "atr_horizon_v2_q90": protocol["tau_atr"],
                "smpr": protocol["tau_smpr"],
                "behavior_label": behavior_value,
                "closed_loop_score": behavior_value,
            },
            {
                "status": "ok",
                "model_family": "LeWM",
                "training_family_id": "synthetic",
                "training_seed": 3073,
                "task": "TwoRoom",
                "training_rho": 0.02,
                "stressor_family": "gaussian",
                "stressor_severity": 0.08,
                "atr_horizon_v2_q90": protocol["tau_atr"],
                "smpr": protocol["tau_smpr"],
                "behavior_label": -behavior_value,
                "closed_loop_score": -behavior_value,
            },
        ],
    }
    path.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def test_external_apply_is_blind_and_does_not_mutate_protocol(
    tmp_path: Path,
) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    out = tmp_path / "blind.csv"
    _diagnostic_input(diagnostics)
    before_bytes = PROTOCOL_PATH.read_bytes()
    before_mtime = PROTOCOL_PATH.stat().st_mtime_ns

    rows, sidecar = apply_protocol(
        protocol_path=PROTOCOL_PATH,
        diagnostics_path=diagnostics,
        out_path=out,
        created_utc="2026-07-10T00:00:00+00:00",
    )

    assert PROTOCOL_PATH.read_bytes() == before_bytes
    assert PROTOCOL_PATH.stat().st_mtime_ns == before_mtime
    protocol_hash = hashlib.sha256(before_bytes).hexdigest()
    assert {row["protocol_sha256"] for row in rows} == {protocol_hash}
    assert sidecar["metadata"]["protocol_hash"] == protocol_hash
    assert sidecar["metadata"]["behavior_blind"] is True
    with out.open(newline="", encoding="utf-8") as stream:
        headers = next(csv.reader(stream))
    assert "behavior_label" not in headers
    assert "closed_loop_score" not in headers
    assert "success" not in " ".join(headers)
    assert all(row["frozen_gate_pass"] == "true" for row in rows)


def test_external_behavior_changes_cannot_change_gate_or_protocol_hash(
    tmp_path: Path,
) -> None:
    diagnostics_a = tmp_path / "diagnostics_a.json"
    diagnostics_b = tmp_path / "diagnostics_b.json"
    _diagnostic_input(diagnostics_a, behavior_value=1.0)
    _diagnostic_input(diagnostics_b, behavior_value=999.0)

    rows_a, _ = apply_protocol(
        protocol_path=PROTOCOL_PATH,
        diagnostics_path=diagnostics_a,
        out_path=tmp_path / "blind_a.csv",
    )
    rows_b, _ = apply_protocol(
        protocol_path=PROTOCOL_PATH,
        diagnostics_path=diagnostics_b,
        out_path=tmp_path / "blind_b.csv",
    )

    fields = (
        "atr_horizon_v2_q90",
        "smpr",
        "atr_threshold_margin",
        "smpr_threshold_margin",
        "joint_score",
        "frozen_gate_pass",
        "protocol_sha256",
    )
    assert [
        tuple(row[field] for field in fields)
        for row in rows_a
    ] == [
        tuple(row[field] for field in fields)
        for row in rows_b
    ]


def test_external_gate_ignores_training_rho_and_accepts_equal_boundaries() -> None:
    protocol = _strict_load(PROTOCOL_PATH)
    values = _joint_values(
        atr=protocol["tau_atr"],
        smpr=protocol["tau_smpr"],
        tau_atr=protocol["tau_atr"],
        tau_smpr=protocol["tau_smpr"],
    )
    assert values[3] is True
    assert values[0] == pytest.approx(0.0)
    assert values[1] == pytest.approx(0.0)

    low_rho = {
        "training_rho": 0.0,
        "atr": protocol["tau_atr"],
        "smpr": protocol["tau_smpr"],
    }
    high_rho = {**low_rho, "training_rho": 0.08}
    low_gate = _joint_values(
        atr=low_rho["atr"],
        smpr=low_rho["smpr"],
        tau_atr=protocol["tau_atr"],
        tau_smpr=protocol["tau_smpr"],
    )[3]
    high_gate = _joint_values(
        atr=high_rho["atr"],
        smpr=high_rho["smpr"],
        tau_atr=protocol["tau_atr"],
        tau_smpr=protocol["tau_smpr"],
    )[3]
    assert low_gate == high_gate


def test_external_apply_rejects_protocol_hash_mismatch(tmp_path: Path) -> None:
    diagnostics = tmp_path / "diagnostics.json"
    _diagnostic_input(diagnostics, protocol_hash="0" * 64)

    with pytest.raises(ValueError, match="protocol hash mismatch"):
        apply_protocol(
            protocol_path=PROTOCOL_PATH,
            diagnostics_path=diagnostics,
            out_path=tmp_path / "blind.csv",
        )


def test_external_module_exposes_no_threshold_override_or_calibration_path() -> None:
    parser = build_external_parser()
    apply_parser = parser._subparsers._group_actions[0].choices["apply"]
    score_parser = parser._subparsers._group_actions[0].choices["score"]
    destinations = {
        action.dest
        for child in (apply_parser, score_parser)
        for action in child._actions
    }
    assert not {"tau_atr", "tau_smpr", "threshold", "calibration"} & destinations

    source = (
        ROOT
        / "paper1"
        / "scripts"
        / "frozen_external_validation.py"
    ).read_text(encoding="utf-8")
    assert "freeze_diagnostic_protocol" not in source
    assert "calibrate_global_gate" not in source


def test_strict_heldout_behavior_rejects_calibration_seed() -> None:
    protocol = _strict_load(PROTOCOL_PATH)
    with pytest.raises(ValueError, match="rejects training seed 3072"):
        _heldout_behavior([EVAL_PATH], protocol)
