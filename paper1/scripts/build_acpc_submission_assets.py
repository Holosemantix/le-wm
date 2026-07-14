#!/usr/bin/env python3
"""Build submission-facing ACPC method/planner figures and compact tables."""

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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLANNER = ROOT / "paper1/results/acpc_planner_stability_v2/summary.json"
DEFAULT_SWEEP = ROOT / "paper1/results/full_sweep_diagnostics_summary.csv"
DEFAULT_METHOD_FIG = ROOT / "assets/paper1_figs/fig_acpc_method.pdf"
DEFAULT_PLANNER_FIG = ROOT / "assets/paper1_figs/fig_acpc_planner_evidence.pdf"
DEFAULT_INCREMENT_TABLE = ROOT / "paper1/tables/table_acpc_planner_increment.tex"
DEFAULT_ABSOLUTE_TABLE = ROOT / "paper1/tables/table_acpc_planner_absolute.tex"
DEFAULT_SWEEP_TABLE = ROOT / "paper1/tables/table_full_sweep_compact.tex"

TASKS = ("TwoRoom", "PushT", "Reacher", "Cube")
TASK_MARKERS = {"TwoRoom": "o", "PushT": "s", "Reacher": "^", "Cube": "D"}
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


def _box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    face: str,
    edge: str,
    fontsize: float = 8.0,
    weight: str = "normal",
) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        fc=face,
        ec=edge,
        lw=0.9,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
    )


def _arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#3D3D3D",
    style: str = "-|>",
    lw: float = 1.0,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=9,
            color=color,
            lw=lw,
            shrinkA=1,
            shrinkB=1,
        )
    )


def plot_method(out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(6.8, 2.55))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        _box(ax, (0.025, 0.60), 0.145, 0.20, "nominal history\n$h$", face="#E8F1F8", edge=ENDPOINT_COLOR, weight="semibold")
        _box(ax, (0.025, 0.22), 0.145, 0.20, "visual probe\n$\\tilde h$", face="#FCEFE7", edge=BASE_COLOR, weight="semibold")
        ax.text(0.098, 0.50, "same underlying state", ha="center", va="center", fontsize=7.2, color="#555555")

        _box(ax, (0.218, 0.41), 0.13, 0.20, "shared encoder\n$E_\\theta$", face="#F4F4F4", edge="#5A5A5A", weight="semibold")
        _arrow(ax, (0.17, 0.70), (0.218, 0.55), color=ENDPOINT_COLOR)
        _arrow(ax, (0.17, 0.32), (0.218, 0.47), color=BASE_COLOR)

        _box(ax, (0.396, 0.41), 0.16, 0.20, "shared actions\n$\\mathbf{a}_{1:H}$ + predictor $F_\\theta$", face="#F1ECF8", edge="#6A51A3", weight="semibold")
        _arrow(ax, (0.348, 0.51), (0.396, 0.51))

        _box(ax, (0.602, 0.60), 0.14, 0.18, "rollout\n$x_{1:H}$", face="#E8F1F8", edge=ENDPOINT_COLOR)
        _box(ax, (0.602, 0.24), 0.14, 0.18, "rollout\n$\\tilde x_{1:H}$", face="#FCEFE7", edge=BASE_COLOR)
        _arrow(ax, (0.556, 0.54), (0.602, 0.67), color=ENDPOINT_COLOR)
        _arrow(ax, (0.556, 0.48), (0.602, 0.35), color=BASE_COLOR)
        ax.annotate(
            "",
            xy=(0.755, 0.66),
            xytext=(0.755, 0.36),
            arrowprops=dict(arrowstyle="<->", color="#2F2F2F", lw=1.1),
        )
        ax.text(0.67, 0.51, "$\\mathrm{ACPC}_H=\\Vert x-\\tilde x\\Vert_2$", ha="center", va="center", fontsize=7.4, fontweight="semibold")

        right_x = 0.80
        _box(ax, (right_x, 0.69), 0.175, 0.19, "future-error drift\n$|\\Delta e|\\leq\\mathrm{ACPC}_H$", face="#EDF7ED", edge="#3A7D44", fontsize=7.6)
        _box(ax, (right_x, 0.405), 0.175, 0.19, "sharp goal-cost bound\n$|\\Delta c_j|\\leq b_j$", face="#FFF7DF", edge="#B8860B", fontsize=7.6)
        _box(ax, (right_x, 0.12), 0.175, 0.19, "planner decision\nregret / margin / elite bounds", face="#F5ECF5", edge="#8C4A8C", fontsize=7.4)
        _arrow(ax, (0.785, 0.60), (right_x, 0.78), color="#3A7D44")
        _arrow(ax, (0.785, 0.51), (right_x, 0.50), color="#B8860B")
        _arrow(ax, (0.785, 0.42), (right_x, 0.215), color="#8C4A8C")

        ax.text(
            0.42,
            0.08,
            "Scoring uses no realized future or behavior label  |  P1: future only evaluates  |  "
            "P2: source tasks $\\to$ remaining tasks  |  P3: Gaussian $\\to$ blur/resize",
            ha="center",
            va="center",
            fontsize=6.8,
            color="#4A4A4A",
        )
        fig.subplots_adjust(left=0.01, right=0.995, bottom=0.02, top=0.98)
        fig.savefig(out, dpi=240)
        plt.close(fig)


def _group_index(summary: dict[str, Any]) -> dict[tuple[str, str, float], dict[str, Any]]:
    return {
        (row["task"], row["checkpoint_role"], float(row["severity"])): row
        for row in summary["group_summary"]
    }


def plot_planner(summary: dict[str, Any], out: Path) -> None:
    index = _group_index(summary)
    analyses = summary["predeclared_incremental_analyses"]
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
            task_values: list[list[float]] = []
            for task in TASKS:
                values = [index[(task, role, s)]["top1_stability_rate"] for s in severities]
                task_values.append(values)
                ax_stability.plot(
                    severities,
                    values,
                    color=color,
                    alpha=0.26,
                    lw=0.8,
                    marker=TASK_MARKERS[task],
                    ms=3.0,
                )
            mean = [sum(values[i] for values in task_values) / len(TASKS) for i in range(3)]
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
            task_values = []
            for task in TASKS:
                values = [math.log10(1 + index[(task, role, s)]["positive_clean_regret_mean"]) for s in severities]
                task_values.append(values)
                ax_regret.plot(
                    severities,
                    values,
                    color=color,
                    alpha=0.26,
                    lw=0.8,
                    marker=TASK_MARKERS[task],
                    ms=3.0,
                )
            mean = [sum(values[i] for values in task_values) / len(TASKS) for i in range(3)]
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
        means = [100 * analyses[key]["lobo_ridge"]["equal_task_relative_mae_reduction"] for key, _ in response_specs]
        bars = ax_increment.bar(x, means, width=0.58, color=["#4C78A8", "#59A14F", "#BAB0AC"], zorder=2)
        for xpos, (key, _) in zip(x, response_specs):
            per_task = analyses[key]["lobo_ridge"]["per_task"]
            offsets = (-0.15, -0.05, 0.05, 0.15)
            for offset, task in zip(offsets, TASKS):
                ax_increment.scatter(
                    xpos + offset,
                    100 * per_task[task]["relative_mae_reduction"],
                    marker=TASK_MARKERS[task],
                    s=18,
                    facecolor="white",
                    edgecolor="#303030",
                    lw=0.65,
                    zorder=3,
                )
        ax_increment.axhline(5, color="#7A3E9D", lw=1.0, ls="--")
        ax_increment.axhline(0, color="#555555", lw=0.7)
        ax_increment.set_xticks(x, [label for _, label in response_specs])
        ax_increment.set_ylabel("MAE reduction from adding 5-step ACPC (%)")
        ax_increment.set_title("(c) Cross-task 5-step increment", loc="left", fontweight="semibold")
        ax_increment.set_ylim(-15, 27)
        ax_increment.text(2.38, 5.8, "5% reference", color="#6A2C8C", ha="right", va="bottom", fontsize=7.0)
        for bar, value in zip(bars, means):
            ax_increment.text(bar.get_x() + bar.get_width() / 2, value + 0.8, f"{value:.1f}", ha="center", va="bottom", fontsize=7.4)
        _polish(ax_increment)

        full_index = {
            (row["task"], row["checkpoint_role"]): row
            for row in summary["full_budget_summary"]
        }
        for task_index, task in enumerate(TASKS):
            base = full_index[(task, "base")]["positive_clean_regret_mean"]
            endpoint = full_index[(task, "endpoint")]["positive_clean_regret_mean"]
            ax_full.plot([0, 1], [base, endpoint], color="#777777", lw=0.9, alpha=0.75)
            ax_full.scatter(0, base, marker=TASK_MARKERS[task], s=31, color=BASE_COLOR, edgecolor="white", lw=0.5, zorder=3)
            ax_full.scatter(1, endpoint, marker=TASK_MARKERS[task], s=31, color=ENDPOINT_COLOR, edgecolor="white", lw=0.5, zorder=3)
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
        r"\caption{Cross-task ridge analysis on 3,200 reduced-budget history records with matched ACPC and planner outcomes. For each evaluation task, models are fitted on the other three tasks. The reference feature set contains severity, base-versus-noise-trained checkpoint identity, candidate-conditioned one-step ACPC, and nominal top-1 margin; the expanded set adds candidate-conditioned five-step ACPC, matching the candidate evaluation horizon. Positive values are reductions in evaluation-task MAE; the final two columns report Spearman rank correlations.}",
        r"\label{tab:acpc-planner-increment}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{5pt}",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Response & MAE reduction & Tasks improved & 1-step Spearman & 5-step Spearman \\",
        r"\midrule",
    ]
    for key, label in specs:
        lobo = analyses[key]["lobo_ridge"]
        spearman = analyses[key]["spearman"]
        value = 100 * lobo["equal_task_relative_mae_reduction"]
        gate = value >= 5 and lobo["tasks_improved"] >= 3
        display = rf"\textbf{{{value:.1f}\%}}" if gate else rf"{value:.1f}\%"
        lines.append(
            f"{label} & {display} & {lobo['tasks_improved']}/4 & "
            f"{spearman['equal_task_h1']:.3f} & {spearman['equal_task_h5']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def build_absolute_table(summary: dict[str, Any]) -> str:
    index = _group_index(summary)
    full = {(row["task"], row["checkpoint_role"]): row for row in summary["full_budget_summary"]}
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Absolute planner outcomes at Gaussian severity 0.08. Reduced-budget rows use 100 independent histories, $K=64$, top-8 elites, and eight CEM steps; full-budget rows use 16 histories, $K=300$, top-30 elites, and 30 steps. Regret evaluates the perturbed action in task-specific squared latent goal-cost units under the clean history; it is not closed-loop return, and magnitudes should not be pooled across tasks.}",
        r"\label{tab:acpc-planner-absolute}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{4.2pt}",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"& \multicolumn{2}{c}{Top-1 stability} & \multicolumn{2}{c}{Reduced regret} & \multicolumn{2}{c}{Full-budget regret} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}",
        r"Task & Base & Endpoint & Base & Endpoint & Base & Endpoint \\",
        r"\midrule",
    ]
    values = []
    for task in TASKS:
        row = [
            index[(task, "base", 0.08)]["top1_stability_rate"],
            index[(task, "endpoint", 0.08)]["top1_stability_rate"],
            index[(task, "base", 0.08)]["positive_clean_regret_mean"],
            index[(task, "endpoint", 0.08)]["positive_clean_regret_mean"],
            full[(task, "base")]["positive_clean_regret_mean"],
            full[(task, "endpoint")]["positive_clean_regret_mean"],
        ]
        values.append(row)
        lines.append(
            f"{task} & {row[0]:.2f} & {row[1]:.2f} & {row[2]:.2f} & {row[3]:.2f} & {row[4]:.2f} & {row[5]:.2f} \\\\"
        )
    means = [sum(row[i] for row in values) / len(values) for i in range(6)]
    lines.extend(
        [
            r"\midrule",
            "Equal-task mean & " + " & ".join(f"{value:.2f}" for value in means) + r" \\",
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
        r"\caption{Compact view of the complete nine-level Gaussian training sweep (three training seeds per level). ``Best'' selects the level with highest mean success under observation noise $\sigma=0.08$; the full trajectories over all nine levels remain in Fig.~\ref{fig:full-sweep-diagnostics}. ATR is divided by each task$\times$seed no-noise value (base $=1$) and is lower-is-better; SMPR remains on its original rate scale and is higher-is-better.}",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--planner-summary", type=Path, default=DEFAULT_PLANNER)
    parser.add_argument("--full-sweep-summary", type=Path, default=DEFAULT_SWEEP)
    parser.add_argument("--method-figure", type=Path, default=DEFAULT_METHOD_FIG)
    parser.add_argument("--planner-figure", type=Path, default=DEFAULT_PLANNER_FIG)
    parser.add_argument("--increment-table", type=Path, default=DEFAULT_INCREMENT_TABLE)
    parser.add_argument("--absolute-table", type=Path, default=DEFAULT_ABSOLUTE_TABLE)
    parser.add_argument("--sweep-table", type=Path, default=DEFAULT_SWEEP_TABLE)
    args = parser.parse_args()

    planner = _load_json(args.planner_summary)
    if planner["validated_shard_count"] != 24 or not planner["invariants"]["pass"]:
        raise SystemExit("planner summary is incomplete or failed invariants")
    plot_method(args.method_figure)
    plot_planner(planner, args.planner_figure)
    _write(args.increment_table, build_increment_table(planner))
    _write(args.absolute_table, build_absolute_table(planner))
    _write(args.sweep_table, build_sweep_table(_read_csv(args.full_sweep_summary)))
    for path in (
        args.method_figure,
        args.planner_figure,
        args.increment_table,
        args.absolute_table,
        args.sweep_table,
    ):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
