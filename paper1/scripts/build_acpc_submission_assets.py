#!/usr/bin/env python3
"""Build submission-facing ACPC planner figure and compact tables."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from paper1.scripts.cross_task_selective_rule import run_all_subsets


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLANNER = ROOT / "paper1/results/acpc_planner_stability_v4/summary.json"
DEFAULT_SWEEP = ROOT / "paper1/results/full_sweep_diagnostics_summary.csv"
DEFAULT_PLANNER_FIG = ROOT / "assets/paper1_figs/fig_acpc_planner_evidence.pdf"
DEFAULT_INCREMENT_TABLE = ROOT / "paper1/tables/table_acpc_planner_increment.tex"
DEFAULT_ABSOLUTE_TABLE = ROOT / "paper1/tables/table_acpc_planner_absolute.tex"
DEFAULT_SWEEP_TABLE = ROOT / "paper1/tables/table_full_sweep_compact.tex"
DEFAULT_PLDM_ROWS = ROOT / "paper1/results/external_validation/pldm_frozen_rows_v2.csv"
DEFAULT_CROSS_TASK_SUMMARY = ROOT / "paper1/results/cross_task_atr_smpr_all_subsets_summary_v1.json"
DEFAULT_PLDM_TABLE = ROOT / "paper1/tables/table_pldm_architecture_portability.tex"

TASKS = ("TwoRoom", "PushT", "Reacher", "Cube")
TASK_MARKERS = {"TwoRoom": "o", "PushT": "s", "Reacher": "^", "Cube": "D"}
SEED_MARKERS = {3072: "o", 3073: "s", 3074: "^"}
BASE_COLOR = "#D55E00"
ENDPOINT_COLOR = "#0072B2"
GRID_COLOR = "#A7A7A7"
STYLE = {
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "axes.linewidth": 0.7,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.2,
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _polish(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", color=GRID_COLOR, alpha=0.24, lw=0.6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _group_index(summary: dict[str, Any]) -> dict[tuple[str, str, float], dict[str, Any]]:
    return {
        (row["task"], row["checkpoint_role"], float(row["severity"])): row
        for row in summary["group_summary"]
    }


def _group_seed_index(
    summary: dict[str, Any],
) -> dict[tuple[int, str, str, float], dict[str, Any]]:
    return {
        (
            int(row["training_seed"]),
            row["task"],
            row["checkpoint_role"],
            float(row["severity"]),
        ): row
        for row in summary["group_seed_summary"]
    }


def plot_planner(summary: dict[str, Any], out: Path) -> None:
    index = _group_index(summary)
    seed_index = _group_seed_index(summary)
    analyses = summary["predeclared_incremental_analyses"]
    seeds = tuple(int(seed) for seed in summary["training_seeds"])
    severities = (0.02, 0.05, 0.08)
    out.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        # The planner panel occupies its own submission float page.  A taller
        # native canvas increases per-panel plotting area and avoids a large
        # unused lower margin after LaTeX places the caption.
        fig, axes = plt.subplots(2, 2, figsize=(6.8, 6.4))
        ax_stability, ax_regret, ax_increment, ax_full = axes.ravel()

        for role, color, label in (
            ("base", BASE_COLOR, "fragile base"),
            ("endpoint", ENDPOINT_COLOR, "noise-trained endpoint"),
        ):
            task_seed_values: list[list[float]] = []
            for seed in seeds:
                for task in TASKS:
                    values = [
                        seed_index[(seed, task, role, s)]["top1_stability_rate"]
                        for s in severities
                    ]
                    task_seed_values.append(values)
                    ax_stability.plot(
                        severities,
                        values,
                        color=color,
                        alpha=0.12,
                        lw=0.65,
                        marker=TASK_MARKERS[task],
                        ms=2.3,
                    )
            mean = [
                sum(values[i] for values in task_seed_values)
                / len(task_seed_values)
                for i in range(3)
            ]
            ax_stability.plot(severities, mean, color=color, lw=2.0, marker="o", ms=4.0, label=label)
        ax_stability.set_title("(a) Fixed-pool top-1 stability", loc="left", fontweight="semibold")
        ax_stability.set_xlabel("probe severity")
        ax_stability.set_ylabel("same-winner rate")
        ax_stability.set_xlim(0.015, 0.085)
        ax_stability.set_ylim(-0.03, 1.03)
        ax_stability.set_xticks(severities)
        ax_stability.legend(frameon=False, loc="lower left")
        _polish(ax_stability)

        for role, color in (("base", BASE_COLOR), ("endpoint", ENDPOINT_COLOR)):
            task_seed_values = []
            for seed in seeds:
                for task in TASKS:
                    values = [
                        math.log10(
                            1
                            + seed_index[(seed, task, role, s)][
                                "positive_clean_regret_mean"
                            ]
                        )
                        for s in severities
                    ]
                    task_seed_values.append(values)
                    ax_regret.plot(
                        severities,
                        values,
                        color=color,
                        alpha=0.12,
                        lw=0.65,
                        marker=TASK_MARKERS[task],
                        ms=2.3,
                    )
            mean = [
                sum(values[i] for values in task_seed_values)
                / len(task_seed_values)
                for i in range(3)
            ]
            ax_regret.plot(severities, mean, color=color, lw=2.0, marker="o", ms=4.0)
        ax_regret.set_title("(b) Adaptive-CEM decision regret", loc="left", fontweight="semibold")
        ax_regret.set_xlabel("probe severity")
        ax_regret.set_ylabel(r"equal-task mean $\log_{10}(1+\mathrm{regret})$")
        ax_regret.set_xlim(0.015, 0.085)
        ax_regret.set_xticks(severities)
        _polish(ax_regret)

        response_specs = (
            ("cost_drift", "cost drift"),
            ("positive_clean_regret", "decision regret"),
            ("first_action_rms", "action RMS"),
        )
        x = list(range(3))
        means = [
            100
            * analyses[key]["three_seed_summary"][
                "relative_mae_reduction_mean"
            ]
            for key, _ in response_specs
        ]
        sds = [
            100
            * analyses[key]["three_seed_summary"][
                "relative_mae_reduction_sample_sd"
            ]
            for key, _ in response_specs
        ]
        bars = ax_increment.bar(x, means, width=0.58, color=["#4C78A8", "#59A14F", "#BAB0AC"], zorder=2)
        ax_increment.errorbar(
            x,
            means,
            yerr=sds,
            fmt="none",
            ecolor="#303030",
            elinewidth=0.9,
            capsize=2.5,
            zorder=4,
        )
        for xpos, (key, _) in zip(x, response_specs):
            offsets = (-0.13, 0.0, 0.13)
            for offset, seed in zip(offsets, seeds):
                value = analyses[key]["per_seed"][str(seed)]["lobo_ridge"][
                    "equal_task_relative_mae_reduction"
                ]
                ax_increment.scatter(
                    xpos + offset,
                    100 * value,
                    marker="o",
                    s=22,
                    facecolor="white",
                    edgecolor="#303030",
                    lw=0.65,
                    zorder=3,
                )
        ax_increment.axhline(5, color="#7A3E9D", lw=1.0, ls="--")
        ax_increment.axhline(0, color="#555555", lw=0.7)
        ax_increment.set_xticks(x, [label for _, label in response_specs])
        ax_increment.set_ylabel("MAE reduction from adding 5-step ACPC (%)")
        ax_increment.set_title("(c) Increment from 5-step ACPC", loc="left", fontweight="semibold")
        ax_increment.set_ylim(-1.5, 20.0)
        ax_increment.text(2.38, 5.5, "5% reference", color="#6A2C8C", ha="right", va="bottom", fontsize=7.0)
        for bar, value, sd in zip(bars, means, sds):
            ax_increment.text(
                bar.get_x() + bar.get_width() / 2,
                value + sd + 0.7,
                f"{value:.1f}$\\pm${sd:.1f}",
                ha="center",
                va="bottom",
                fontsize=7.2,
            )
        _polish(ax_increment)

        full_index = {
            (row["task"], row["checkpoint_role"]): row
            for row in summary["full_budget_summary"]
        }
        full_seed_index = {
            (int(row["training_seed"]), row["task"], row["checkpoint_role"]): row
            for row in summary["full_budget_seed_summary"]
        }
        seed_offsets = {seed: offset for seed, offset in zip(seeds, (-0.045, 0.0, 0.045))}
        for task in TASKS:
            for seed in seeds:
                base_seed = full_seed_index[(seed, task, "base")][
                    "positive_clean_regret_mean"
                ]
                endpoint_seed = full_seed_index[(seed, task, "endpoint")][
                    "positive_clean_regret_mean"
                ]
                offset = seed_offsets[seed]
                ax_full.plot(
                    [offset, 1 + offset],
                    [base_seed, endpoint_seed],
                    color="#777777",
                    lw=0.55,
                    alpha=0.28,
                )
                ax_full.scatter(
                    offset,
                    base_seed,
                    marker=TASK_MARKERS[task],
                    s=15,
                    color=BASE_COLOR,
                    alpha=0.38,
                    edgecolor="none",
                    zorder=2,
                )
                ax_full.scatter(
                    1 + offset,
                    endpoint_seed,
                    marker=TASK_MARKERS[task],
                    s=15,
                    color=ENDPOINT_COLOR,
                    alpha=0.38,
                    edgecolor="none",
                    zorder=2,
                )
            base = full_index[(task, "base")]["positive_clean_regret_mean"]
            endpoint = full_index[(task, "endpoint")]["positive_clean_regret_mean"]
            ax_full.plot([0, 1], [base, endpoint], color="#555555", lw=1.05, alpha=0.82)
            ax_full.scatter(0, base, marker=TASK_MARKERS[task], s=34, color=BASE_COLOR, edgecolor="white", lw=0.5, zorder=3)
            ax_full.scatter(1, endpoint, marker=TASK_MARKERS[task], s=34, color=ENDPOINT_COLOR, edgecolor="white", lw=0.5, zorder=3)
        ax_full.set_yscale("log")
        ax_full.set_xlim(-0.35, 1.35)
        ax_full.set_xticks([0, 1], ["fragile base", "endpoint"])
        ax_full.set_ylabel("positive regret (log scale)")
        ax_full.set_title(r"(d) Full budget: $K=300$, 30 CEM steps", loc="left", fontweight="semibold")
        task_handles = [
            Line2D([], [], marker=TASK_MARKERS[task], color="#555555", ls="none", label=task, ms=4.5)
            for task in TASKS
        ]
        ax_full.legend(handles=task_handles, ncol=2, frameon=False, loc="lower left")
        _polish(ax_full)

        fig.subplots_adjust(left=0.09, right=0.985, bottom=0.08, top=0.965, wspace=0.30, hspace=0.30)
        fig.savefig(out, dpi=240)
        plt.close(fig)


def build_increment_table(summary: dict[str, Any]) -> str:
    analyses = summary["predeclared_incremental_analyses"]
    specs = (
        ("cost_drift", "Fixed-pool max cost drift"),
        ("positive_clean_regret", "Adaptive positive decision regret"),
        ("first_action_rms", "Adaptive first-action RMS"),
    )
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Cross-task ridge analysis on 9,600 matched reduced-budget history records. Models are fitted separately within each training run on three tasks and evaluated on the fourth. The reference features are severity, checkpoint role, candidate-conditioned one-step ACPC, and nominal top-1 margin; the expanded model adds candidate-conditioned five-step ACPC. Entries are equal-task MAE reductions; mean $\pm$ sample SD treats the training run as the model-replication unit, and the final column counts improving task--run evaluations.}",
        r"\label{tab:acpc-planner-increment}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.7pt}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Response & Mean $\pm$ SD & Run range & Cells improved \\",
        r"\midrule",
    ]
    for key, label in specs:
        aggregate = analyses[key]["three_seed_summary"]
        mean = 100 * aggregate["relative_mae_reduction_mean"]
        sd = 100 * aggregate["relative_mae_reduction_sample_sd"]
        mean_display = f"{mean:.1f} $\\pm$ {sd:.1f}\\%"
        run_range = (
            f"{100 * aggregate['relative_mae_reduction_min']:.1f}--"
            f"{100 * aggregate['relative_mae_reduction_max']:.1f}\\%"
        )
        lines.append(
            f"{label} & {mean_display} & {run_range} & "
            f"{aggregate['task_seed_cells_improved']}/12 \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def build_absolute_table(summary: dict[str, Any]) -> str:
    index = _group_index(summary)
    full = {(row["task"], row["checkpoint_role"]): row for row in summary["full_budget_summary"]}
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Absolute planner outcomes at Gaussian severity 0.08, reported as mean $\pm$ sample SD across independent training runs after histories are averaged within run. Reduced-budget rows use 100 histories, $K=64$, top-8 elites, and eight CEM steps; full-budget rows evaluate the same 16 fixed histories per task across roles and runs with $K=300$, top-30 elites, and 30 steps. Regret is clean-history squared latent goal-cost, not closed-loop return, and its scale is task specific.}",
        r"\label{tab:acpc-planner-absolute}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.2pt}",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"& \multicolumn{2}{c}{Top-1 stability} & \multicolumn{2}{c}{Reduced regret} & \multicolumn{2}{c}{Full-budget regret} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}",
        r"Task & Base & Endpoint & Base & Endpoint & Base & Endpoint \\",
        r"\midrule",
    ]
    def cell(record: dict[str, Any], field: str) -> str:
        return (
            f"{record[field]:.2f}$\\pm$"
            f"{record[field + '_sample_sd']:.2f}"
        )

    for task in TASKS:
        cells = [
            cell(index[(task, "base", 0.08)], "top1_stability_rate"),
            cell(index[(task, "endpoint", 0.08)], "top1_stability_rate"),
            cell(index[(task, "base", 0.08)], "positive_clean_regret_mean"),
            cell(index[(task, "endpoint", 0.08)], "positive_clean_regret_mean"),
            cell(full[(task, "base")], "positive_clean_regret_mean"),
            cell(full[(task, "endpoint")], "positive_clean_regret_mean"),
        ]
        lines.append(f"{task} & {' & '.join(cells)} \\\\")

    group_seed_rows = summary["group_seed_summary"]
    full_seed_rows = summary["full_budget_seed_summary"]

    def seed_macro(
        rows: list[dict[str, Any]],
        *,
        role: str,
        field: str,
        severity: float | None = None,
    ) -> str:
        values = []
        for seed in summary["training_seeds"]:
            selected = [
                row
                for row in rows
                if int(row["training_seed"]) == int(seed)
                and row["checkpoint_role"] == role
                and (severity is None or float(row["severity"]) == severity)
            ]
            if len(selected) != len(TASKS):
                raise ValueError("planner seed macro lacks four tasks")
            values.append(sum(float(row[field]) for row in selected) / len(TASKS))
        mean = sum(values) / len(values)
        sd = math.sqrt(
            sum((value - mean) ** 2 for value in values) / (len(values) - 1)
        )
        return f"{mean:.2f}$\\pm${sd:.2f}"

    means = [
        seed_macro(
            group_seed_rows,
            role="base",
            field="top1_stability_rate",
            severity=0.08,
        ),
        seed_macro(
            group_seed_rows,
            role="endpoint",
            field="top1_stability_rate",
            severity=0.08,
        ),
        seed_macro(
            group_seed_rows,
            role="base",
            field="positive_clean_regret_mean",
            severity=0.08,
        ),
        seed_macro(
            group_seed_rows,
            role="endpoint",
            field="positive_clean_regret_mean",
            severity=0.08,
        ),
        seed_macro(full_seed_rows, role="base", field="positive_clean_regret_mean"),
        seed_macro(
            full_seed_rows,
            role="endpoint",
            field="positive_clean_regret_mean",
        ),
    ]
    lines.extend(
        [
            r"\midrule",
            "Equal-task mean & " + " & ".join(means) + r" \\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines)


def build_sweep_table(rows: list[dict[str, str]]) -> str:
    by_task = {task: [row for row in rows if row["task"] == task] for task in TASKS}
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Compact view of the complete nine-level Gaussian training sweep. ``Best'' selects the level with highest mean success under observation noise $\sigma=0.08$; the full trajectories over all nine levels remain in Fig.~\ref{fig:full-sweep-diagnostics}. ATR is divided by each task$\times$run no-noise value (base $=1$) and is lower-is-better; SMPR remains on its original rate scale and is higher-is-better.}",
        r"\label{tab:full-sweep-compact}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Task & Base success (\%) & Best success (\%) & Best $\sigma_{\max}$ & ATR: base $\to$ best & SMPR: base $\to$ best & Majority-recovered levels \\",
        r"\midrule",
    ]
    for task in TASKS:
        task_rows = sorted(by_task[task], key=lambda row: float(row["rho"]))
        base = next(row for row in task_rows if abs(float(row["rho"])) < 1e-12)
        best = max(task_rows, key=lambda row: float(row["obs_sigma_008_score_mean"]))
        recovered = [float(row["rho"]) for row in task_rows if float(row["recovery_label_rate"]) >= 0.5]
        recovery_text = "--" if not recovered else f"{min(recovered):.2f}--{max(recovered):.2f}"
        lines.append(
            f"{task} & {float(base['obs_sigma_008_score_mean']):.1f} & "
            f"{float(best['obs_sigma_008_score_mean']):.1f} & {float(best['rho']):.2f} & "
            f"{float(base['atr_normalized_q90_mean']):.2f}$\\to${float(best['atr_normalized_q90_mean']):.2f} & "
            f"{float(base['smpr_delta0_mean']):.2f}$\\to${float(best['smpr_delta0_mean']):.2f} & "
            f"{recovery_text} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def build_pldm_table(
    frozen_rows: list[dict[str, str]],
    lewm_cross_task_summary: dict[str, Any],
) -> str:
    """Compare PLDM-local calibration with score-aligned LeWM transfer."""
    if len(frozen_rows) != 36 or {
        row.get("model_family") for row in frozen_rows
    } != {"PLDM"}:
        raise ValueError("PLDM frozen validation is incomplete")

    seeds = sorted({int(float(row["training_seed"])) for row in frozen_rows})
    observed = {
        (row["task"], int(round(100 * float(row["training_rho"]))))
        for row in frozen_rows
    }
    expected = {(task, rho) for task in TASKS for rho in range(9)}
    if len(seeds) != 1 or observed != expected:
        raise ValueError("PLDM sweep must contain one complete four-task grid")

    base_atr: dict[str, float] = {}
    for task in TASKS:
        base = [
            row
            for row in frozen_rows
            if row["task"] == task and abs(float(row["training_rho"])) < 1e-12
        ]
        if len(base) != 1 or float(base[0]["atr_horizon_v2_q90"]) <= 0:
            raise ValueError(f"invalid PLDM ATR reference for {task}")
        base_atr[task] = float(base[0]["atr_horizon_v2_q90"])

    local_rows = [
        {
            "task": row["task"],
            "training_seed": seeds[0],
            "rho": float(row["training_rho"]),
            "atr_normalized_q90": (
                float(row["atr_horizon_v2_q90"]) / base_atr[row["task"]]
            ),
            "smpr_delta0": float(row["smpr"]),
            "recovery_label": row["behavior_label"],
        }
        for row in frozen_rows
    ]
    details, _, local_summary = run_all_subsets(
        local_rows, expected_seeds=seeds
    )
    local_eval = [row for row in details if row["source_coverage"] == 3]
    if len(local_eval) != len(TASKS):
        raise ValueError("PLDM leave-one-task-out analysis is incomplete")

    local_confusion = {
        key: sum(int(row[key]) for row in local_eval)
        for key in ("tp", "tn", "fp", "fn")
    }

    def pooled(confusion: dict[str, int]) -> tuple[float, float, float]:
        tp, tn = confusion["tp"], confusion["tn"]
        fp, fn = confusion["fp"], confusion["fn"]
        recall = tp / (tp + fn)
        specificity = tn / (tn + fp)
        precision = tp / (tp + fp)
        return 0.5 * (recall + specificity), precision, recall

    local_ba, local_precision, local_recall = pooled(local_confusion)

    lewm_thresholds: dict[str, tuple[float, float]] = {}
    for partition in lewm_cross_task_summary.get("partitions", []):
        if (
            int(partition.get("source_coverage", -1)) == 3
            and len(partition.get("evaluation_tasks", [])) == 1
        ):
            task = str(partition["evaluation_tasks"][0])
            lewm_thresholds[task] = (
                float(partition["tau_atr"]),
                float(partition["tau_smpr"]),
            )
    if set(lewm_thresholds) != set(TASKS):
        raise ValueError("LeWM three-source thresholds are incomplete")

    relative_lewm_confusion = {key: 0 for key in ("tp", "tn", "fp", "fn")}
    for row in local_rows:
        tau_atr, tau_smpr = lewm_thresholds[str(row["task"])]
        truth = str(row["recovery_label"]).lower() == "true"
        pred = (
            float(row["atr_normalized_q90"]) <= tau_atr
            and float(row["smpr_delta0"]) >= tau_smpr
        )
        key = "tp" if truth and pred else "fn" if truth else "fp" if pred else "tn"
        relative_lewm_confusion[key] += 1
    relative_ba, relative_precision, relative_recall = pooled(
        relative_lewm_confusion
    )

    if not any(
        item["source_coverage"] == 3 for item in local_summary["coverage"]
    ):
        raise ValueError("PLDM three-source summary is missing")

    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{PLDM architecture-portability check on the complete four-task, nine-checkpoint Gaussian sweep. Both rows use the current task-relative ATR score: thresholds are selected on the other three PLDM tasks or transferred from the corresponding LeWM split. Metrics pool all 36 evaluation rows. Raw numerical thresholds are not assumed to be shared across model families.}",
        r"\label{tab:pldm-architecture-portability}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{4.0pt}",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Calibration & BA & Precision & Recall & False pass & False miss \\",
        r"\midrule",
        (
            f"PLDM-local, other three tasks & {local_ba:.3f} & "
            f"{local_precision:.3f} & {local_recall:.3f} & "
            f"{local_confusion['fp']} & {local_confusion['fn']} \\\\"
        ),
        (
            f"LeWM-source reference, PLDM-anchored & {relative_ba:.3f} & "
            f"{relative_precision:.3f} & {relative_recall:.3f} & "
            f"{relative_lewm_confusion['fp']} & "
            f"{relative_lewm_confusion['fn']} \\\\"
        ),
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--planner-summary", type=Path, default=DEFAULT_PLANNER)
    parser.add_argument("--full-sweep-summary", type=Path, default=DEFAULT_SWEEP)
    parser.add_argument("--planner-figure", type=Path, default=DEFAULT_PLANNER_FIG)
    parser.add_argument("--increment-table", type=Path, default=DEFAULT_INCREMENT_TABLE)
    parser.add_argument("--absolute-table", type=Path, default=DEFAULT_ABSOLUTE_TABLE)
    parser.add_argument("--sweep-table", type=Path, default=DEFAULT_SWEEP_TABLE)
    parser.add_argument("--pldm-rows", type=Path, default=DEFAULT_PLDM_ROWS)
    parser.add_argument(
        "--cross-task-summary", type=Path, default=DEFAULT_CROSS_TASK_SUMMARY
    )
    parser.add_argument("--pldm-table", type=Path, default=DEFAULT_PLDM_TABLE)
    args = parser.parse_args()

    planner = _load_json(args.planner_summary)
    if (
        planner["validated_shard_count"] != 72
        or planner.get("training_seeds") != [3072, 3073, 3074]
        or not planner["invariants"]["pass"]
    ):
        raise SystemExit("planner summary is incomplete or failed invariants")
    plot_planner(planner, args.planner_figure)
    _write(args.increment_table, build_increment_table(planner))
    _write(args.absolute_table, build_absolute_table(planner))
    _write(args.sweep_table, build_sweep_table(_read_csv(args.full_sweep_summary)))
    _write(
        args.pldm_table,
        build_pldm_table(
            _read_csv(args.pldm_rows),
            _load_json(args.cross_task_summary),
        ),
    )
    for path in (
        args.planner_figure,
        args.increment_table,
        args.absolute_table,
        args.sweep_table,
        args.pldm_table,
    ):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
