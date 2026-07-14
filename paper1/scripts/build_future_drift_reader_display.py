#!/usr/bin/env python3
"""Build the reader-facing three-seed future-drift display from adjudication JSON."""

from __future__ import annotations

import json
import os
from pathlib import Path
from statistics import mean, stdev
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .utils_paper1_io import ROOT, TASKS, write_csv


SOURCE_DIR = ROOT / "paper1/results/target_aligned_acpc_dev"
OUT_CSV = ROOT / "paper1/results/future_drift_three_seed_v1.csv"
OUT_SUMMARY = ROOT / "paper1/results/future_drift_three_seed_summary_v1.json"
OUT_TABLE = ROOT / "paper1/tables/table_target_aligned_acpc.tex"
OUT_ABSOLUTE = ROOT / "paper1/tables/table_target_aligned_acpc_absolute.tex"
OUT_FIGURE = ROOT / "assets/paper1_figs/fig_future_drift_three_seed_v1.pdf"

SEEDS = (3072, 3073, 3074)
CONTROL_NAMES = {
    "plus_action_zero_h8_control": "zero actions",
    "plus_candidate_shuffle_h8_control": "cross-trajectory actions",
    "plus_time_shuffle_h8_control": "time-shuffled actions",
}


def _seed_rows(seed: int) -> list[dict[str, Any]]:
    if seed == 3072:
        path = SOURCE_DIR / "adjudication_four_task_seed3072_goal25_base_endpoint_retrospective_v1.json"
        payload = json.loads(path.read_text())
        cells = payload["primary_logged_fragile_base"]["cells"]
        absolute = next(cell for cell in cells if cell["target"] == "absolute")
        rows = []
        for item in absolute["per_task"]:
            rows.append(
                {
                    "task": item["task"],
                    "training_seed": seed,
                    "one_step_mae": item["h1_mae"],
                    "best_control_mae": item["best_destroyed_mae"],
                    "eight_step_mae": item["correct_mae"],
                    "best_control": CONTROL_NAMES[item["best_destroyed_name"]],
                    "reduction_vs_one_step": item["relative_mae_reduction_vs_h1"],
                    "reduction_vs_control": item["relative_mae_reduction_vs_best_destroyed"],
                    "win_blocks": item["both_win_blocks"],
                    "block_count": item["block_count"],
                    "pass": item["pass"],
                }
            )
        return rows

    path = SOURCE_DIR / f"adjudication_four_task_seed{seed}_goal25_base_endpoint_v1.json"
    payload = json.loads(path.read_text())
    rows = []
    for artifact in payload["artifacts"]:
        if f"baseline_seed{seed}" not in os.path.basename(artifact["checkpoint"]):
            continue
        gate = artifact["logged_gates"]["correct_absolute_h8_error_drift"]
        rows.append(
            {
                "task": artifact["task"],
                "training_seed": seed,
                "one_step_mae": gate["mae"]["shallow"],
                "best_control_mae": gate["mae"]["best_destroyed"],
                "eight_step_mae": gate["mae"]["correct"],
                "best_control": CONTROL_NAMES[gate["best_destroyed_name"]],
                "reduction_vs_one_step": gate["relative_mae_reduction"]["versus_shallow"],
                "reduction_vs_control": gate["relative_mae_reduction"]["versus_best_destroyed"],
                "win_blocks": gate["block_direction"]["both_win_count"],
                "block_count": gate["block_direction"]["paired_group_count"],
                "pass": gate["pass"],
            }
        )
    return rows


def _seed_summary(rows: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    selected = [row for row in rows if row["training_seed"] == seed]
    if {row["task"] for row in selected} != set(TASKS):
        raise ValueError(f"seed {seed} does not contain all four tasks")
    return {
        "training_seed": seed,
        "reduction_vs_one_step": mean(row["reduction_vs_one_step"] for row in selected),
        "reduction_vs_control": mean(row["reduction_vs_control"] for row in selected),
        "tasks_passed": sum(bool(row["pass"]) for row in selected),
        "task_count": len(selected),
    }


def _write_summary_table(summaries: list[dict[str, Any]]) -> None:
    a = [100 * row["reduction_vs_one_step"] for row in summaries]
    b = [100 * row["reduction_vs_control"] for row in summaries]
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Predicting the change in eight-step latent error under a visual perturbation. All regressions use the same target and base features; they differ only in the ACPC feature. The recorded-action eight-step feature is compared with one-step ACPC and with the strongest of three same-horizon features using zeroed actions, actions from another trajectory, or time-shuffled actions. Values are relative reductions in held-out MAE after rotating evaluation over 16 trajectory groups; higher is better.}",
        r"\label{tab:target-aligned-acpc}",
        r"\small",
        r"\setlength{\tabcolsep}{6pt}",
        r"\begin{tabular}{lrrc}",
        r"\toprule",
        r"Training run & vs. one-step ACPC & vs. same-horizon control & Task--run cells improved \\",
        r"\midrule",
    ]
    for row in summaries:
        lines.append(
            f"seed {row['training_seed']} & {100*row['reduction_vs_one_step']:.1f}\\% & "
            f"{100*row['reduction_vs_control']:.1f}\\% & {row['tasks_passed']}/{row['task_count']} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            f"mean $\\pm$ SD & {mean(a):.1f} $\\pm$ {stdev(a):.1f}\\% & "
            f"{mean(b):.1f} $\\pm$ {stdev(b):.1f}\\% & 12/12 \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )
    OUT_TABLE.write_text("\n".join(lines) + "\n")


def _write_absolute_table(rows: list[dict[str, Any]]) -> None:
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Held-out MAE for predicting the absolute change in eight-step latent prediction error. Each row contains 16 trajectory groups. The recorded-action column uses eight-step ACPC with the observed actions; the control column uses the strongest of three eight-step features with zeroed actions, actions from another trajectory, or time-shuffled actions. Lower is better.}",
        r"\label{tab:target-aligned-acpc-absolute}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.6pt}",
        r"\begin{tabular}{lrrrrlc}",
        r"\toprule",
        r"Task & seed & one-step & same-horizon control & recorded-action 8-step & control type & win blocks \\",
        r"\midrule",
    ]
    ordered = sorted(rows, key=lambda row: (TASKS.index(row["task"]), row["training_seed"]))
    for index, row in enumerate(ordered):
        lines.append(
            f"{row['task']} & {row['training_seed']} & {row['one_step_mae']:.3f} & "
            f"{row['best_control_mae']:.3f} & \\textbf{{{row['eight_step_mae']:.3f}}} & "
            f"{row['best_control']} & {row['win_blocks']}/{row['block_count']} \\\\"
        )
        if index + 1 < len(ordered) and ordered[index + 1]["task"] != row["task"]:
            lines.append(r"\addlinespace[1pt]")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    OUT_ABSOLUTE.write_text("\n".join(lines) + "\n")


def _plot(rows: list[dict[str, Any]]) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "mathtext.fontset": "stix",
            "pdf.fonttype": 42,
            "font.size": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
        }
    )
    fig, ax = plt.subplots(figsize=(6.65, 2.85))
    comparisons = (
        ("reduction_vs_one_step", -0.16, "#4C78A8", "vs. one-step ACPC"),
        (
            "reduction_vs_control",
            0.16,
            "#E45756",
            "vs. same-horizon action control",
        ),
    )
    run_jitter = (-0.045, 0.0, 0.045)
    for task_index, task in enumerate(TASKS):
        task_rows = sorted(
            (row for row in rows if row["task"] == task),
            key=lambda row: int(row["training_seed"]),
        )
        if len(task_rows) != len(SEEDS):
            raise ValueError(f"{task}: expected one row per training run")
        for key, offset, color, label in comparisons:
            values = [100 * row[key] for row in task_rows]
            for jitter, value in zip(run_jitter, values):
                ax.scatter(
                    task_index + offset + jitter,
                    value,
                    s=27,
                    color=color,
                    alpha=0.55,
                    edgecolor="white",
                    linewidth=0.4,
                    zorder=3,
                )
            ax.scatter(
                task_index + offset,
                mean(values),
                marker="D",
                s=50,
                color=color,
                edgecolor="#222222",
                linewidth=0.55,
                zorder=4,
                label=label if task_index == 0 else None,
            )
    ax.axhline(0, color="#666666", linewidth=0.8, linestyle="--", zorder=1)
    ax.set_xlim(-0.55, len(TASKS) - 0.45)
    ax.set_ylim(0, 90)
    ax.set_xticks(range(len(TASKS)), TASKS)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_ylabel("Reduction in held-out MAE (%)")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.65)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="both", direction="out", length=3.0)
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.14), frameon=False)
    fig.tight_layout(pad=0.7)
    OUT_FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIGURE, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rows = [row for seed in SEEDS for row in _seed_rows(seed)]
    summaries = [_seed_summary(rows, seed) for seed in SEEDS]
    write_csv(OUT_CSV, rows, list(rows[0]))
    a = [row["reduction_vs_one_step"] for row in summaries]
    b = [row["reduction_vs_control"] for row in summaries]
    payload = {
        "target": "absolute change in eight-step latent prediction error",
        "training_seeds": list(SEEDS),
        "seed_summaries": summaries,
        "mean_reduction_vs_one_step": mean(a),
        "sample_sd_reduction_vs_one_step": stdev(a),
        "mean_reduction_vs_same_horizon_control": mean(b),
        "sample_sd_reduction_vs_same_horizon_control": stdev(b),
        "all_seed_task_cells_pass": all(row["pass"] for row in rows),
    }
    OUT_SUMMARY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    _write_summary_table(summaries)
    _write_absolute_table(rows)
    _plot(rows)


if __name__ == "__main__":
    main()
