#!/usr/bin/env python3
"""Build isolated paper-v2 draft displays from the frozen three-seed summary."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/paper1_v2_matplotlib")

import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    REPO_ROOT
    / "paper1/results/high_severity_ir_sr_multiseed_v1/analysis/"
    / "seeds_3072_3073_3074/summary.json"
)
ROWS_SOURCE = SOURCE.with_name("ir_sr_rows_joined.csv")
OUT_ROOT = Path(__file__).resolve().parents[1]
FIGURE_ROOT = OUT_ROOT / "figures"
TABLE_ROOT = OUT_ROOT / "tables"
SOURCE_MAP = OUT_ROOT / "source_map.json"

EXPECTED = {
    "row_count": 384,
    "training_seeds": [3072, 3073, 3074],
    "tasks": ["TwoRoom", "PushT", "Reacher", "Cube"],
    "evaluation_sigma": [0.08, 0.16, 0.32, 0.64],
    "ir_threshold": 0.3,
    "sr_threshold": 0.95,
    "source_sha256": "8cbed858644ce3cf4502cce88118a01d976b093b57ffc49307bdc8c33c035505",
    "rows_source_sha256": "1dd4f2a7d2efe493dc3bdbdea6d7baa6272993d5fc703b00e70ef8fd67b60d27",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load() -> dict:
    assert _sha256(SOURCE) == EXPECTED["source_sha256"]
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert payload["row_count"] == EXPECTED["row_count"]
    assert payload["training_seeds"] == EXPECTED["training_seeds"]
    assert payload["tasks"] == EXPECTED["tasks"]
    assert payload["evaluation_sigma"] == EXPECTED["evaluation_sigma"]
    assert payload["thresholds"]["ir_relative_max"] == EXPECTED["ir_threshold"]
    assert payload["thresholds"]["sr_min"] == EXPECTED["sr_threshold"]
    assert payload["scope"]["threshold_or_pair_rule_retuning"] is False
    assert payload["scope"]["posthoc_selector"] is False
    assert payload["scope"]["no_argmax_or_optimum_analysis"] is True
    return payload


def _load_rows() -> list[dict[str, str]]:
    assert _sha256(ROWS_SOURCE) == EXPECTED["rows_source_sha256"]
    with ROWS_SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == EXPECTED["row_count"]
    return rows


def _is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def _veto_breakdown(rows: list[dict[str, str]]) -> dict:
    result: dict[str, dict] = {}
    veto_keys: dict[str, set[tuple[str, int, float]]] = {}
    for sigma_eval in EXPECTED["evaluation_sigma"]:
        label = str(sigma_eval)
        selected = [
            row
            for row in rows
            if float(row["sigma_eval"]) == sigma_eval
            and _is_true(row["natural_sr_veto"])
        ]
        by_task = {
            task: sum(row["task"] == task for row in selected)
            for task in EXPECTED["tasks"]
        }
        sigma_max_values = sorted({float(row["sigma_max"]) for row in selected})
        by_training_sigma = {
            str(value): sum(float(row["sigma_max"]) == value for row in selected)
            for value in sigma_max_values
        }
        veto_keys[label] = {
            (row["task"], int(row["training_seed"]), float(row["sigma_max"]))
            for row in selected
        }
        result[label] = {
            "count": len(selected),
            "by_task": by_task,
            "training_sigma_max_values": sigma_max_values,
            "by_training_sigma": by_training_sigma,
        }

    assert veto_keys["0.08"] == veto_keys["0.16"]
    assert result["0.08"]["by_task"] == {
        "TwoRoom": 3,
        "PushT": 0,
        "Reacher": 0,
        "Cube": 0,
    }
    assert result["0.32"]["by_task"] == {
        "TwoRoom": 4,
        "PushT": 5,
        "Reacher": 1,
        "Cube": 0,
    }
    assert result["0.64"]["by_task"] == {
        "TwoRoom": 5,
        "PushT": 6,
        "Reacher": 0,
        "Cube": 0,
    }
    return result


def _build_activation_figure(payload: dict) -> dict:
    rows = payload["decision_summary_by_sigma_eval"]["by_sigma_eval"]
    sigmas = EXPECTED["evaluation_sigma"]
    entries = [rows[str(value)] for value in sigmas]

    total = np.array([entry["row_instance_count"] for entry in entries])
    joint = np.array([entry["joint_pass_count"] for entry in entries])
    veto = np.array([entry["natural_sr_veto_count"] for entry in entries])
    ir_reject = total - np.array([entry["ir_pass_count"] for entry in entries])
    ir_pass = joint + veto
    ir_pass_rate = 100.0 * ir_pass / total
    joint_pass_rate = 100.0 * joint / total
    assert np.all(total == 96)
    assert np.all(joint + veto + ir_reject == total)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 10,
            "axes.labelsize": 10,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
        }
    )
    fig, ax = plt.subplots(figsize=(5.8, 3.0), constrained_layout=True)
    x = np.arange(len(sigmas))
    ir_line = ax.plot(
        x,
        ir_pass_rate,
        color="#4C78A8",
        marker="o",
        markersize=5.5,
        linewidth=2.0,
        label="Passes IR",
        zorder=4,
    )[0]
    joint_line = ax.plot(
        x,
        joint_pass_rate,
        color="#E68613",
        marker="s",
        markersize=5.2,
        linewidth=1.9,
        linestyle="--",
        label="Passes IR and SR",
        zorder=4,
    )[0]
    ax.fill_between(
        x,
        joint_pass_rate,
        ir_pass_rate,
        color="#F2A541",
        alpha=0.22,
        label="Additional SR veto",
        zorder=2,
    )

    ax.set_xticks(x, [f"{value:.2f}" for value in sigmas])
    ax.set_xlabel(r"Evaluation noise $\sigma_{\mathrm{eval}}$")
    ax.set_ylabel("Checkpoint rows passing (\%)")
    ax.set_ylim(0, 104)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.grid(axis="y", color="#DDDDDD", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        handles=[ir_line, joint_line],
        loc="lower left",
        frameon=False,
        fontsize=8.8,
    )

    FIGURE_ROOT.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURE_ROOT / "fig_sr_guard_activation_by_severity.pdf"
    png_path = FIGURE_ROOT / "fig_sr_guard_activation_by_severity.png"
    fig.savefig(
        pdf_path,
        bbox_inches="tight",
        metadata={"CreationDate": None, "ModDate": None},
    )
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    plt.close(fig)

    return {
        "pdf": str(pdf_path.relative_to(REPO_ROOT)),
        "pdf_sha256": _sha256(pdf_path),
        "png": str(png_path.relative_to(REPO_ROOT)),
        "png_sha256": _sha256(png_path),
        "counts": {
            str(sigma): {
                "joint_pass": int(joint[index]),
                "sr_veto": int(veto[index]),
                "ir_reject": int(ir_reject[index]),
                "total": int(total[index]),
            }
            for index, sigma in enumerate(sigmas)
        },
    }


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _interval(record: dict) -> str:
    return f"[{_fmt(record['task_minimum'])}, {_fmt(record['task_maximum'])}]"


def _build_association_table(payload: dict) -> dict:
    ranks = payload["rank_association_summary"]
    exposure = payload["exposure_comparator_summary"][
        "retention_pp__direct_spearman"
    ]
    ir_direct = ranks["retention_pp__neg_ir_relative_q90__direct_spearman"]
    ir_adjusted = ranks[
        "retention_pp__neg_ir_relative_q90__exposure_adjusted_partial_spearman"
    ]
    sr_direct = ranks["retention_pp__sr__direct_spearman"]
    sr_adjusted = ranks[
        "retention_pp__sr__exposure_adjusted_partial_spearman"
    ]
    ir_ratio_direct = ranks[
        "retention_ratio__neg_ir_relative_q90__direct_spearman"
    ]
    ir_ratio_adjusted = ranks[
        "retention_ratio__neg_ir_relative_q90__exposure_adjusted_partial_spearman"
    ]
    sr_ratio_direct = ranks["retention_ratio__sr__direct_spearman"]
    sr_ratio_adjusted = ranks[
        "retention_ratio__sr__exposure_adjusted_partial_spearman"
    ]

    table = rf"""\begin{{table}}[!htb]
\centering
\caption{{Descriptive Spearman associations with same-checkpoint retention
(success under noise minus clean success) in the separate broad-severity
experiment. Within each task and training run, all quantities are
double-centered over the $8\times4$ training--evaluation severity grid.
Training-run correlations are then averaged within each task, and tasks receive
equal weight. The adjusted column reports partial Spearman correlation after
residualizing the rank-transformed diagnostic and outcome against the
rank-transformed exposure ratio
$-\sigma_{{\mathrm{{eval}}}}/\sigma_{{\max}}$ within each task--run block.
Ranges contain the four task means, not confidence intervals. The exposure
ratio is a simple metadata comparator, not an exhaustive baseline, and these
associations do not establish checkpoint-selection accuracy.}}
\label{{tab:multiseverity-associations}}
\small
\begin{{tabular}}{{lcccc}}
\toprule
Quantity (favorable direction) & Direct $\rho$ & Task range & Adjusted $\rho$ & Task range \\
\midrule
$-\sigma_{{\mathrm{{eval}}}}/\sigma_{{\max}}$ & {_fmt(exposure['equal_task_mean'])} & {_interval(exposure)} & -- & -- \\
$-\mathrm{{IR}}^{{\mathrm{{rel}}}}$ & {_fmt(ir_direct['equal_task_mean'])} & {_interval(ir_direct)} & {_fmt(ir_adjusted['equal_task_mean'])} & {_interval(ir_adjusted)} \\
SR & {_fmt(sr_direct['equal_task_mean'])} & {_interval(sr_direct)} & {_fmt(sr_adjusted['equal_task_mean'])} & {_interval(sr_adjusted)} \\
\bottomrule
\end{{tabular}}
\end{{table}}
"""
    TABLE_ROOT.mkdir(parents=True, exist_ok=True)
    output = TABLE_ROOT / "table_multiseverity_associations.tex"
    output.write_text(table, encoding="utf-8")
    return {
        "path": str(output.relative_to(REPO_ROOT)),
        "sha256": _sha256(output),
        "values": {
            "exposure_direct": exposure["equal_task_mean"],
            "ir_direct": ir_direct["equal_task_mean"],
            "ir_exposure_adjusted": ir_adjusted["equal_task_mean"],
            "sr_direct": sr_direct["equal_task_mean"],
            "sr_exposure_adjusted": sr_adjusted["equal_task_mean"],
            "ir_ratio_direct": ir_ratio_direct["equal_task_mean"],
            "ir_ratio_exposure_adjusted": ir_ratio_adjusted["equal_task_mean"],
            "sr_ratio_direct": sr_ratio_direct["equal_task_mean"],
            "sr_ratio_exposure_adjusted": sr_ratio_adjusted["equal_task_mean"],
        },
    }


def _build_number_macros(
    figure: dict,
    table: dict,
    veto_breakdown: dict,
    rows: list[dict[str, str]],
) -> dict:
    values = table["values"]
    counts = figure["counts"]
    minimum_clean_success = min(float(row["clean_success"]) for row in rows)
    assert minimum_clean_success > 0
    macro_text = rf"""% Generated by scripts/build_draft_assets.py; do not edit.
\providecommand{{\vTwoCheckpointCount}}{{96}}
\providecommand{{\vTwoRowCount}}{{384}}
\providecommand{{\vTwoTaskCount}}{{4}}
\providecommand{{\vTwoRunCount}}{{3}}
\providecommand{{\vTwoTrainLevelCount}}{{8}}
\providecommand{{\vTwoEvalLevelCount}}{{4}}
\providecommand{{\vTwoFactorialCellCount}}{{32}}
\providecommand{{\vTwoInteractionDf}}{{21}}
\providecommand{{\vTwoTrainSigmaSet}}{{\{{0.1,0.2,0.3,0.4,0.5,0.7,1.0,1.5\}}}}
\providecommand{{\vTwoEvalSigmaSet}}{{\{{0.08,0.16,0.32,0.64\}}}}
\providecommand{{\vTwoEvalZeroEight}}{{0.08}}
\providecommand{{\vTwoEvalZeroSixteen}}{{0.16}}
\providecommand{{\vTwoEvalZeroThirtyTwo}}{{0.32}}
\providecommand{{\vTwoEvalZeroSixtyFour}}{{0.64}}
\providecommand{{\vTwoTrainOne}}{{1.0}}
\providecommand{{\vTwoTrainOneFive}}{{1.5}}
\providecommand{{\vTwoIRThreshold}}{{0.3}}
\providecommand{{\vTwoSRThreshold}}{{0.95}}
\providecommand{{\vTwoVetoAtZeroEight}}{{{counts['0.08']['sr_veto']}}}
\providecommand{{\vTwoIRPassAtZeroEight}}{{{counts['0.08']['joint_pass'] + counts['0.08']['sr_veto']}}}
\providecommand{{\vTwoJointPassAtZeroEight}}{{{counts['0.08']['joint_pass']}}}
\providecommand{{\vTwoVetoAtZeroSixteen}}{{{counts['0.16']['sr_veto']}}}
\providecommand{{\vTwoIRPassAtZeroSixteen}}{{{counts['0.16']['joint_pass'] + counts['0.16']['sr_veto']}}}
\providecommand{{\vTwoJointPassAtZeroSixteen}}{{{counts['0.16']['joint_pass']}}}
\providecommand{{\vTwoVetoAtZeroThirtyTwo}}{{{counts['0.32']['sr_veto']}}}
\providecommand{{\vTwoIRPassAtZeroThirtyTwo}}{{{counts['0.32']['joint_pass'] + counts['0.32']['sr_veto']}}}
\providecommand{{\vTwoJointPassAtZeroThirtyTwo}}{{{counts['0.32']['joint_pass']}}}
\providecommand{{\vTwoVetoAtZeroSixtyFour}}{{{counts['0.64']['sr_veto']}}}
\providecommand{{\vTwoIRPassAtZeroSixtyFour}}{{{counts['0.64']['joint_pass'] + counts['0.64']['sr_veto']}}}
\providecommand{{\vTwoJointPassAtZeroSixtyFour}}{{{counts['0.64']['joint_pass']}}}
\providecommand{{\vTwoLowVetoAtOne}}{{{veto_breakdown['0.08']['by_training_sigma']['1.0']}}}
\providecommand{{\vTwoLowVetoAtOneFive}}{{{veto_breakdown['0.08']['by_training_sigma']['1.5']}}}
\providecommand{{\vTwoVetoThirtyTwoTwoRoom}}{{{veto_breakdown['0.32']['by_task']['TwoRoom']}}}
\providecommand{{\vTwoVetoThirtyTwoPushT}}{{{veto_breakdown['0.32']['by_task']['PushT']}}}
\providecommand{{\vTwoVetoThirtyTwoReacher}}{{{veto_breakdown['0.32']['by_task']['Reacher']}}}
\providecommand{{\vTwoVetoThirtyTwoCube}}{{{veto_breakdown['0.32']['by_task']['Cube']}}}
\providecommand{{\vTwoVetoSixtyFourTwoRoom}}{{{veto_breakdown['0.64']['by_task']['TwoRoom']}}}
\providecommand{{\vTwoVetoSixtyFourPushT}}{{{veto_breakdown['0.64']['by_task']['PushT']}}}
\providecommand{{\vTwoVetoSixtyFourReacher}}{{{veto_breakdown['0.64']['by_task']['Reacher']}}}
\providecommand{{\vTwoVetoSixtyFourCube}}{{{veto_breakdown['0.64']['by_task']['Cube']}}}
\providecommand{{\vTwoExposureDirect}}{{{_fmt(values['exposure_direct'])}}}
\providecommand{{\vTwoIRDirect}}{{{_fmt(values['ir_direct'])}}}
\providecommand{{\vTwoSRDirect}}{{{_fmt(values['sr_direct'])}}}
\providecommand{{\vTwoIRAdjusted}}{{{_fmt(values['ir_exposure_adjusted'])}}}
\providecommand{{\vTwoSRAdjusted}}{{{_fmt(values['sr_exposure_adjusted'])}}}
\providecommand{{\vTwoIRRatioDirect}}{{{_fmt(values['ir_ratio_direct'])}}}
\providecommand{{\vTwoSRRatioDirect}}{{{_fmt(values['sr_ratio_direct'])}}}
\providecommand{{\vTwoIRRatioAdjusted}}{{{_fmt(values['ir_ratio_exposure_adjusted'])}}}
\providecommand{{\vTwoSRRatioAdjusted}}{{{_fmt(values['sr_ratio_exposure_adjusted'])}}}
\providecommand{{\vTwoMinimumCleanSuccess}}{{{minimum_clean_success:g}}}
"""
    output = TABLE_ROOT / "multiseverity_numbers.tex"
    output.write_text(macro_text, encoding="utf-8")
    return {
        "path": str(output.relative_to(REPO_ROOT)),
        "sha256": _sha256(output),
        "minimum_clean_success": minimum_clean_success,
    }


def main() -> None:
    payload = _load()
    rows = _load_rows()
    figure = _build_activation_figure(payload)
    table = _build_association_table(payload)
    veto_breakdown = _veto_breakdown(rows)
    macros = _build_number_macros(figure, table, veto_breakdown, rows)
    source_map = {
        "schema_version": "paper1-v2-high-severity-draft-1.0",
        "source": str(SOURCE.relative_to(REPO_ROOT)),
        "source_sha256": _sha256(SOURCE),
        "rows_source": str(ROWS_SOURCE.relative_to(REPO_ROOT)),
        "rows_source_sha256": _sha256(ROWS_SOURCE),
        "figure": figure,
        "table": table,
        "number_macros": macros,
        "sr_veto_breakdown": veto_breakdown,
        "claim_boundary": {
            "descriptive_only": True,
            "no_threshold_retuning": True,
            "no_selector_utility_claim": True,
            "no_optimal_training_severity_claim": True,
            "not_a_homogeneous_extension_of_the_original_narrow_sweep": True,
        },
    }
    SOURCE_MAP.write_text(
        json.dumps(source_map, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
