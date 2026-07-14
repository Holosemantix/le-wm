#!/usr/bin/env python3
"""Evaluate the ATR+SMPR rule across every source/evaluation task partition."""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .utils_paper1_io import ROOT, SEEDS, TASKS, fnum, read_csv, write_csv


DEFAULT_DIAGNOSTICS = ROOT / "paper1/results/full_sweep_diagnostics.csv"
DEFAULT_ROWS = ROOT / "paper1/results/cross_task_atr_smpr_all_subsets_v1.csv"
DEFAULT_PARAMS = ROOT / "paper1/results/cross_task_atr_smpr_all_subsets_params_v1.json"
DEFAULT_SUMMARY = ROOT / "paper1/results/cross_task_atr_smpr_all_subsets_summary_v1.json"
DEFAULT_TABLE = ROOT / "paper1/tables/table_cross_task_atr_smpr_all_subsets_v1.tex"
DEFAULT_FIGURE = ROOT / "assets/paper1_figs/fig_cross_task_atr_smpr_source_coverage_v1.pdf"

TAU_ATR = (0.05, 0.075, 0.10, 0.15, 0.20, 0.30)
TAU_SMPR = (0.80, 0.85, 0.90, 0.95)

DETAIL_FIELDS = [
    "partition_id",
    "source_coverage",
    "source_tasks",
    "evaluation_tasks",
    "tau_atr",
    "tau_smpr",
    "task",
    "training_seed",
    "behavioral_start",
    "predicted_start",
    "start_error",
    "abs_start_error",
    "false_early",
    "false_late",
    "balanced_accuracy",
    "precision",
    "recall",
    "f1",
    "tp",
    "tn",
    "fp",
    "fn",
    "num_rows",
]

METRICS = ("balanced_accuracy", "precision", "recall", "f1", "abs_start_error")

STYLE = {
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "axes.linewidth": 0.7,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
}


def _truth(row: dict[str, Any]) -> bool:
    return str(row.get("recovery_label", "")).lower() == "true"


def _pred(row: dict[str, Any], tau_atr: float, tau_smpr: float) -> bool:
    return (
        fnum(row["atr_normalized_q90"]) <= tau_atr
        and fnum(row["smpr_delta0"]) >= tau_smpr
    )


def _blocks(rows: Iterable[dict[str, Any]]) -> dict[tuple[str, int], list[dict[str, Any]]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["task"], int(float(row["training_seed"])))].append(row)
    return {
        key: sorted(block, key=lambda row: fnum(row["rho"]))
        for key, block in grouped.items()
    }


def _start(rows: list[dict[str, Any]], predicate: Any) -> float | None:
    values = [fnum(row["rho"]) for row in rows if predicate(row)]
    return min(values) if values else None


def _safe_mean(values: Iterable[Any]) -> float:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return mean(finite) if finite else math.nan


def _safe_max(values: Iterable[Any]) -> float:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    return max(finite) if finite else math.nan


def _json_number(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if value is None:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _block_eval(
    rows: list[dict[str, Any]], tau_atr: float, tau_smpr: float
) -> dict[str, Any]:
    truth = [_truth(row) for row in rows]
    pred = [_pred(row, tau_atr, tau_smpr) for row in rows]
    behavioral_start = _start(rows, _truth)
    predicted_start = _start(rows, lambda row: _pred(row, tau_atr, tau_smpr))

    if behavioral_start is None and predicted_start is None:
        start_error = 0.0
    elif behavioral_start is None:
        start_error = -1.0
    elif predicted_start is None:
        start_error = 1.0
    else:
        start_error = predicted_start - behavioral_start

    tp = sum(actual and estimate for actual, estimate in zip(truth, pred))
    tn = sum((not actual) and (not estimate) for actual, estimate in zip(truth, pred))
    fp = sum((not actual) and estimate for actual, estimate in zip(truth, pred))
    fn = sum(actual and (not estimate) for actual, estimate in zip(truth, pred))

    sensitivity = tp / (tp + fn) if tp + fn else math.nan
    specificity = tn / (tn + fp) if tn + fp else math.nan
    if math.isfinite(sensitivity) and math.isfinite(specificity):
        balanced_accuracy = 0.5 * (sensitivity + specificity)
    elif math.isfinite(sensitivity):
        balanced_accuracy = sensitivity
    elif math.isfinite(specificity):
        balanced_accuracy = specificity
    else:
        balanced_accuracy = math.nan
    precision = tp / (tp + fp) if tp + fp else math.nan
    recall = sensitivity
    f1 = (
        2 * precision * recall / (precision + recall)
        if math.isfinite(precision) and math.isfinite(recall) and precision + recall
        else math.nan
    )

    false_early = 0
    false_late = 0
    if behavioral_start is not None:
        false_early = sum(
            estimate and fnum(row["rho"]) < behavioral_start
            for row, estimate in zip(rows, pred)
        )
        false_late = sum(
            actual and not estimate for actual, estimate in zip(truth, pred)
        )

    return {
        "behavioral_start": behavioral_start,
        "predicted_start": predicted_start,
        "start_error": start_error,
        "abs_start_error": abs(start_error),
        "false_early": int(false_early),
        "false_late": int(false_late),
        "balanced_accuracy": balanced_accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "num_rows": len(rows),
    }


def _objective(
    blocks: dict[tuple[str, int], list[dict[str, Any]]],
    tau_atr: float,
    tau_smpr: float,
) -> tuple[float, int, int, float, float, float]:
    evaluations = [
        _block_eval(rows, tau_atr, tau_smpr) for rows in blocks.values()
    ]
    return (
        _safe_mean(item["abs_start_error"] for item in evaluations),
        sum(item["false_early"] for item in evaluations),
        sum(item["false_late"] for item in evaluations),
        -_safe_mean(item["balanced_accuracy"] for item in evaluations),
        tau_atr,
        -tau_smpr,
    )


def _candidate_thresholds() -> Iterable[tuple[float, float]]:
    return itertools.product(TAU_ATR, TAU_SMPR)


def _task_set_text(tasks: Iterable[str]) -> str:
    return "|".join(task for task in TASKS if task in set(tasks))


def _partition_id(source: tuple[str, ...]) -> str:
    slug = "_".join(task.lower() for task in source)
    return f"src{len(source)}_{slug}"


def _validate_input(
    rows: list[dict[str, Any]], expected_seeds: Iterable[int] = SEEDS
) -> None:
    seeds = tuple(int(seed) for seed in expected_seeds)
    expected = {
        (task, seed, f"{rho / 100:.2f}")
        for task in TASKS
        for seed in seeds
        for rho in range(9)
    }
    observed = {
        (row["task"], int(float(row["training_seed"])), f"{fnum(row['rho']):.2f}")
        for row in rows
    }
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise ValueError(
            f"diagnostic grid mismatch: missing={missing[:8]}, extra={extra[:8]}"
        )
    for field in ("atr_normalized_q90", "smpr_delta0", "recovery_label"):
        if any(row.get(field, "") == "" for row in rows):
            raise ValueError(f"missing required field {field!r}")


def _task_means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["task"])].append(row)
    return {
        task: {metric: _safe_mean(row[metric] for row in task_rows) for metric in METRICS}
        for task, task_rows in grouped.items()
    }


def _partition_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    task_means = _task_means(rows)
    return {
        "balanced_accuracy": _safe_mean(item["balanced_accuracy"] for item in task_means.values()),
        "precision": _safe_mean(item["precision"] for item in task_means.values()),
        "recall": _safe_mean(item["recall"] for item in task_means.values()),
        "f1": _safe_mean(item["f1"] for item in task_means.values()),
        "mean_abs_start_error": _safe_mean(item["abs_start_error"] for item in task_means.values()),
        "max_abs_start_error": _safe_max(row["abs_start_error"] for row in rows),
        "evaluation_task_metrics": task_means,
    }


def run_all_subsets(
    rows: list[dict[str, Any]],
    *,
    expected_seeds: Iterable[int] = SEEDS,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    seeds = tuple(int(seed) for seed in expected_seeds)
    _validate_input(rows, seeds)
    all_details: list[dict[str, Any]] = []
    split_params: list[dict[str, Any]] = []
    partition_summaries: list[dict[str, Any]] = []

    for coverage in (1, 2, 3):
        for source in itertools.combinations(TASKS, coverage):
            source_set = set(source)
            evaluation = tuple(task for task in TASKS if task not in source_set)
            source_rows = [row for row in rows if row["task"] in source_set]
            evaluation_rows = [row for row in rows if row["task"] not in source_set]
            source_blocks = _blocks(source_rows)
            best = min(
                _candidate_thresholds(),
                key=lambda threshold: _objective(source_blocks, *threshold),
            )
            tau_atr, tau_smpr = best
            objective = _objective(source_blocks, tau_atr, tau_smpr)
            partition_id = _partition_id(source)
            source_text = _task_set_text(source)
            evaluation_text = _task_set_text(evaluation)

            details: list[dict[str, Any]] = []
            for (task, seed), block in _blocks(evaluation_rows).items():
                record = {
                    "partition_id": partition_id,
                    "source_coverage": coverage,
                    "source_tasks": source_text,
                    "evaluation_tasks": evaluation_text,
                    "tau_atr": tau_atr,
                    "tau_smpr": tau_smpr,
                    "task": task,
                    "training_seed": seed,
                    **_block_eval(block, tau_atr, tau_smpr),
                }
                details.append(record)
                all_details.append(record)

            partition_metrics = _partition_summary(details)
            partition_summaries.append(
                {
                    "partition_id": partition_id,
                    "source_coverage": coverage,
                    "source_tasks": list(source),
                    "evaluation_tasks": list(evaluation),
                    "tau_atr": tau_atr,
                    "tau_smpr": tau_smpr,
                    **partition_metrics,
                }
            )
            split_params.append(
                {
                    "partition_id": partition_id,
                    "source_coverage": coverage,
                    "source_tasks": list(source),
                    "evaluation_tasks": list(evaluation),
                    "source_rows": len(source_rows),
                    "evaluation_rows": len(evaluation_rows),
                    "source_task_seed_blocks": len(source_blocks),
                    "evaluation_task_seed_blocks": len(_blocks(evaluation_rows)),
                    "selected_thresholds": {
                        "tau_atr": tau_atr,
                        "tau_smpr": tau_smpr,
                    },
                    "selection_objective": {
                        "mean_abs_start_error": objective[0],
                        "false_early": objective[1],
                        "false_late": objective[2],
                        "negative_macro_balanced_accuracy": objective[3],
                        "tau_atr_tiebreak": objective[4],
                        "negative_tau_smpr_tiebreak": objective[5],
                    },
                }
            )

    coverage_summaries: list[dict[str, Any]] = []
    for coverage in (1, 2, 3):
        coverage_rows = [row for row in all_details if row["source_coverage"] == coverage]
        task_means = _task_means(coverage_rows)
        splits = [item for item in partition_summaries if item["source_coverage"] == coverage]
        threshold_counts = Counter(
            (float(item["tau_atr"]), float(item["tau_smpr"])) for item in splits
        )
        coverage_summaries.append(
            {
                "source_coverage": coverage,
                "partition_count": len(splits),
                "evaluation_task_incidence_count": sum(len(item["evaluation_tasks"]) for item in splits),
                "balanced_accuracy": _safe_mean(item["balanced_accuracy"] for item in task_means.values()),
                "precision": _safe_mean(item["precision"] for item in task_means.values()),
                "recall": _safe_mean(item["recall"] for item in task_means.values()),
                "f1": _safe_mean(item["f1"] for item in task_means.values()),
                "mean_abs_start_error": _safe_mean(item["abs_start_error"] for item in task_means.values()),
                "max_abs_start_error": _safe_max(row["abs_start_error"] for row in coverage_rows),
                "partition_balanced_accuracy_range": [
                    min(item["balanced_accuracy"] for item in splits),
                    max(item["balanced_accuracy"] for item in splits),
                ],
                "partition_mean_abs_start_error_range": [
                    min(item["mean_abs_start_error"] for item in splits),
                    max(item["mean_abs_start_error"] for item in splits),
                ],
                "selected_threshold_counts": [
                    {"tau_atr": key[0], "tau_smpr": key[1], "count": count}
                    for key, count in sorted(threshold_counts.items())
                ],
                "evaluation_task_metrics": task_means,
            }
        )

    params = {
        "schema_version": "paper1-cross-task-selective-rule-params-1.0",
        "rule": "ATR_rel <= tau_atr AND SMPR >= tau_smpr",
        "task_order": TASKS,
        "training_seeds": seeds,
        "checkpoint_grid": [f"{rho / 100:.2f}" for rho in range(9)],
        "candidate_grid": {"tau_atr": TAU_ATR, "tau_smpr": TAU_SMPR},
        "selection_objective_order": [
            "mean_abs_start_error",
            "false_early",
            "false_late",
            "negative_macro_balanced_accuracy",
            "tau_atr",
            "negative_tau_smpr",
        ],
        "evaluation_outcomes_used_for_selection": False,
        "splits": split_params,
    }
    summary = {
        "schema_version": "paper1-cross-task-selective-rule-summary-1.0",
        "aggregation": (
            "mean over training-seed blocks within evaluation task; mean over eligible "
            "source subsets within coverage; equal mean over four evaluation tasks"
        ),
        "partitions_are_independent_samples": False,
        "detail_row_count": len(all_details),
        "partition_count": len(partition_summaries),
        "evaluation_task_incidence_count": sum(
            len(item["evaluation_tasks"]) for item in partition_summaries
        ),
        "partitions": partition_summaries,
        "coverage": coverage_summaries,
    }
    return all_details, params, summary


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, bool):
        return value
    if isinstance(value, (float, int)):
        return _json_number(value)
    return value


def write_table(summary: dict[str, Any], out: Path) -> None:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Cross-task portability of the selective ACPC rule. Thresholds are selected only on the source tasks and applied unchanged to the evaluation tasks. Metrics first average three training runs within each task. Onset errors use training-noise-grid units. This table evaluates threshold portability, not individual diagnostic components.}",
        r"\label{tab:cross-task-all-subsets}",
        r"\small",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabular}{>{\raggedright\arraybackslash}p{0.17\textwidth}>{\raggedright\arraybackslash}p{0.17\textwidth}rrrrr}",
        r"\toprule",
        r"Source tasks & Evaluation tasks & $\tau_R$ & $\tau_M$ & BA & P / R & \shortstack{Onset error\\mean / max} \\",
        r"\midrule",
    ]
    for item in summary["partitions"]:
        source = ", ".join(item["source_tasks"])
        evaluation = ", ".join(item["evaluation_tasks"])
        lines.append(
            f"{source} & {evaluation} & {item['tau_atr']:.3g} & {item['tau_smpr']:.2f} & "
            f"{item['balanced_accuracy']:.3f} & {item['precision']:.3f} / {item['recall']:.3f} & "
            f"{item['mean_abs_start_error']:.3f} / {item['max_abs_start_error']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_source_coverage(summary: dict[str, Any], out: Path) -> None:
    individual_color = "#7A7A7A"
    summary_color = "#0072B2"
    grid_color = "#B7B7B7"
    out.parent.mkdir(parents=True, exist_ok=True)

    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.55))
        metrics = (
            ("balanced_accuracy", "(a) Evaluation-task accuracy", "Balanced accuracy"),
            ("mean_abs_start_error", "(b) Recovery onset", "Mean absolute onset error"),
        )
        for ax, (metric, title, ylabel) in zip(axes, metrics):
            for coverage in (1, 2, 3):
                partitions = [
                    item for item in summary["partitions"] if item["source_coverage"] == coverage
                ]
                offsets = (
                    [0.0]
                    if len(partitions) == 1
                    else [
                        -0.14 + index * (0.28 / (len(partitions) - 1))
                        for index in range(len(partitions))
                    ]
                )
                values = [item[metric] for item in partitions]
                ax.scatter(
                    [coverage + offset for offset in offsets],
                    values,
                    s=22,
                    color=individual_color,
                    alpha=0.72,
                    edgecolor="white",
                    linewidth=0.35,
                    zorder=2,
                )
                coverage_summary = next(
                    item for item in summary["coverage"] if item["source_coverage"] == coverage
                )
                ax.scatter(
                    [coverage],
                    [coverage_summary[metric]],
                    s=52,
                    facecolor="white",
                    edgecolor=summary_color,
                    linewidth=1.5,
                    marker="D",
                    zorder=3,
                )
            ax.set_title(title, loc="left", fontweight="semibold")
            ax.set_xlabel("Number of source tasks")
            ax.set_ylabel(ylabel)
            ax.set_xticks((1, 2, 3))
            ax.set_xlim(0.65, 3.35)
            ax.grid(True, axis="y", color=grid_color, alpha=0.35, lw=0.6)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
        axes[0].axhline(0.5, color="#A0A0A0", lw=0.7, ls="--", zorder=1)
        axes[0].text(3.31, 0.505, "chance", ha="right", va="bottom", fontsize=6.8, color="#666666")
        axes[1].text(
            0.02,
            0.98,
            "training-noise-grid units",
            transform=axes[1].transAxes,
            ha="left",
            va="top",
            fontsize=6.8,
            color="#555555",
        )
        fig.legend(
            handles=[
                plt.Line2D([], [], marker="o", ls="", color=individual_color, label="source subset"),
                plt.Line2D(
                    [],
                    [],
                    marker="D",
                    ls="",
                    markerfacecolor="white",
                    markeredgecolor=summary_color,
                    label="task-equal summary",
                ),
            ],
            loc="lower center",
            ncol=2,
            frameon=False,
            bbox_to_anchor=(0.5, -0.015),
        )
        fig.subplots_adjust(left=0.09, right=0.985, top=0.90, bottom=0.27, wspace=0.32)
        fig.savefig(out)
        plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostics", type=Path, default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--rows-out", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--params-out", type=Path, default=DEFAULT_PARAMS)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--table-out", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--figure-out", type=Path, default=DEFAULT_FIGURE)
    args = parser.parse_args()

    details, params, summary = run_all_subsets(read_csv(args.diagnostics))
    csv_rows = [
        {
            key: "" if isinstance(value, float) and not math.isfinite(value) else value
            for key, value in row.items()
        }
        for row in details
    ]
    write_csv(args.rows_out, csv_rows, DETAIL_FIELDS)
    args.params_out.parent.mkdir(parents=True, exist_ok=True)
    args.params_out.write_text(
        json.dumps(_json_ready(params), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(
        json.dumps(_json_ready(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_table(summary, args.table_out)
    plot_source_coverage(summary, args.figure_out)

    print(f"wrote {args.rows_out} ({len(details)} task-seed rows)")
    print(f"wrote {args.params_out}")
    print(f"wrote {args.summary_out}")
    print(f"wrote {args.table_out}")
    print(f"wrote {args.figure_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
