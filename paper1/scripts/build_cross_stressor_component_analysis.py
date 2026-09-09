#!/usr/bin/env python3
"""Build a descriptive, component-only cross-stressor analysis.

The input is the frozen 24-row cross-stressor artifact.  This script reports
the two diagnostic components separately:

* ``ir_improvement = 1 - endpoint_ir_relative`` (the base value is 1); and
* ``sr_change = endpoint_sr - base_sr``.

It deliberately does not construct a scalar combination of the components.
The paired rows are checkpoint/stressor observations, not IID samples, so all
cluster-level summaries are labelled descriptively.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[2]
TASKS = ("TwoRoom", "PushT", "Reacher", "Cube")
SEEDS = (3072, 3073, 3074)
STRESSORS = ("blur", "resize")

DEFAULT_SOURCE = ROOT / "paper1/results/external_validation/cross_stressor_three_source_ir_sr_v2.csv"
DEFAULT_ROWS = ROOT / "paper1/results/external_validation/cross_stressor_components_v1.csv"
DEFAULT_SUMMARY = ROOT / "paper1/results/external_validation/cross_stressor_components_v1.json"
DEFAULT_TABLE = ROOT / "paper1/tables/table_cross_stressor_components_v1.tex"
DEFAULT_APPENDIX = ROOT / "paper1/tables/table_cross_stressor_components_all_pairs_v1.tex"
DEFAULT_FIGURE = ROOT / "assets/paper1_figs/fig_cross_stressor_components_v1.pdf"
DEFAULT_FIGURE_PNG = ROOT / "assets/paper1_figs/fig_cross_stressor_components_v1.png"

OUTPUT_FIELDS = [
    "task",
    "training_seed",
    "stressor",
    "ir_threshold",
    "sr_threshold",
    "base_stressed_score",
    "endpoint_stressed_score",
    "delta_behavior",
    "behavior_class",
    "observed_positive",
    "base_ir_relative",
    "endpoint_ir_relative",
    "ir_improvement",
    "base_sr",
    "endpoint_sr",
    "sr_change",
    "endpoint_ir_pass",
    "endpoint_sr_pass",
    "ir_pass_sr_reject_veto",
]

PLOT_STYLE = {
    "font.family": "serif",
    "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7.2,
    "ytick.labelsize": 7.2,
    "legend.fontsize": 7.0,
}

TASK_LABELS = {
    "TwoRoom": "TwoRoom",
    "PushT": "PushT",
    "Reacher": "Reacher",
    "Cube": "Cube",
}
STRESSOR_LABELS = {"blur": "Blur", "resize": "Resize"}
STRESSOR_COLORS = {"blur": "#377eb8", "resize": "#e69f00"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _float(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite numeric value: {value!r}")
    return number


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return mean(values) if values else None


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average_rank = ((start + 1) + end) / 2.0
        for index in order[start:end]:
            ranks[index] = average_rank
        start = end
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right)
    )
    denominator = math.sqrt(
        sum((value - left_mean) ** 2 for value in left)
        * sum((value - right_mean) ** 2 for value in right)
    )
    return numerator / denominator if denominator else None


def _spearman(left: list[float], right: list[float]) -> float | None:
    return _pearson(_rank(left), _rank(right))


def _linear_quantile(sorted_values: list[float], quantile: float) -> float | None:
    """Use the linear-interpolation convention of build_scalar_score_diagnosis."""
    if not sorted_values:
        return None
    position = quantile * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (
        position - lower
    )


def _exact_cluster_resample(
    per_task: dict[str, tuple[list[float], list[float]]],
) -> tuple[list[float], int]:
    """Enumerate ordered task-cluster draws exactly, matching the scalar audit."""
    tasks = sorted(per_task)
    values: list[float] = []
    degenerate = 0
    for draw in itertools.product(tasks, repeat=len(tasks)):
        component_values: list[float] = []
        behavior_values: list[float] = []
        for task in draw:
            task_component, task_behavior = per_task[task]
            component_values += task_component
            behavior_values += task_behavior
        rho = _spearman(component_values, behavior_values)
        if rho is None:
            degenerate += 1
        else:
            values.append(rho)
    values.sort()
    return values, degenerate


def _cluster_resampling_for_component(
    rows: list[dict[str, Any]], component: str
) -> dict[str, Any]:
    per_task = {
        task: (
            [float(row[component]) for row in rows if row["task"] == task],
            [float(row["delta_behavior"]) for row in rows if row["task"] == task],
        )
        for task in TASKS
    }
    draws, degenerate = _exact_cluster_resample(per_task)
    negative = sum(value < 0.0 for value in draws)
    return {
        "ordered_draws": len(TASKS) ** len(TASKS),
        "finite_draws": len(draws),
        "p2_5": _linear_quantile(draws, 0.025),
        "p50": _linear_quantile(draws, 0.50),
        "p97_5": _linear_quantile(draws, 0.975),
        "negative_correlation_count": negative,
        "degenerate_count": degenerate,
    }


def _confusion(rows: list[dict[str, Any]], component: str) -> dict[str, Any]:
    """Compare a positive component change with the predefined positive label."""
    predicted = [row[component] > 0.0 for row in rows]
    target = [bool(row["observed_positive"]) for row in rows]
    tp = sum(pred and truth for pred, truth in zip(predicted, target))
    tn = sum((not pred) and (not truth) for pred, truth in zip(predicted, target))
    fp = sum(pred and (not truth) for pred, truth in zip(predicted, target))
    fn = sum((not pred) and truth for pred, truth in zip(predicted, target))
    n = len(rows)
    behavior_sign_agreement = sum(
        (row[component] > 0.0) == (row["delta_behavior"] > 0.0) for row in rows
    )
    return {
        "positive_change_n": int(sum(predicted)),
        "zero_or_negative_change_n": int(n - sum(predicted)),
        "sign_agreement": (tp + tn) / n if n else None,
        "behavior_sign_agreement": behavior_sign_agreement / n if n else None,
        "confusion_vs_positive_behavior_label": {
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
        },
    }


def _component_metrics(rows: list[dict[str, Any]], component: str) -> dict[str, Any]:
    values = [float(row[component]) for row in rows]
    behavior = [float(row["delta_behavior"]) for row in rows]
    result = {
        "n": len(rows),
        "mean": _mean(values),
        "median": median(values) if values else None,
        "spearman_delta_behavior": _spearman(behavior, values),
    }
    result.update(_confusion(rows, component))
    return result


def _gate_metrics(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "endpoint_ir_pass_n": int(sum(row["endpoint_ir_pass"] for row in rows)),
        "endpoint_sr_pass_n": int(sum(row["endpoint_sr_pass"] for row in rows)),
        "ir_pass_sr_reject_veto_n": int(
            sum(row["ir_pass_sr_reject_veto"] for row in rows)
        ),
    }


def _scope_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "task_clusters": sorted({row["task"] for row in rows}, key=TASKS.index),
        "stressor_levels": sorted({row["stressor"] for row in rows}, key=STRESSORS.index),
        "mean_delta_behavior": _mean(row["delta_behavior"] for row in rows),
        "ir_improvement": _component_metrics(rows, "ir_improvement"),
        "sr_change": _component_metrics(rows, "sr_change"),
        "absolute_endpoint_gate": _gate_metrics(rows),
    }


def _loto_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_heldout: dict[str, dict[str, Any]] = {}
    for heldout in TASKS:
        remaining = [row for row in rows if row["task"] != heldout]
        by_heldout[heldout] = {
            "n": len(remaining),
            "task_clusters": sorted({row["task"] for row in remaining}, key=TASKS.index),
            "ir_improvement_spearman": _component_metrics(
                remaining, "ir_improvement"
            )["spearman_delta_behavior"],
            "sr_change_spearman": _component_metrics(remaining, "sr_change")[
                "spearman_delta_behavior"
            ],
        }

    def _value_range(key: str) -> list[float | None]:
        values = [item[key] for item in by_heldout.values() if item[key] is not None]
        return [min(values), max(values)] if values else [None, None]

    return {
        "definition": "Each value recomputes pooled Spearman after omitting one task cluster; n=18 rows per remaining set.",
        "by_heldout_task": by_heldout,
        "spearman_range": {
            "ir_improvement": _value_range("ir_improvement_spearman"),
            "sr_change": _value_range("sr_change_spearman"),
        },
    }


def _validate_source(rows: list[dict[str, str]]) -> None:
    if len(rows) != 24:
        raise ValueError(f"expected 24 canonical rows, found {len(rows)}")
    expected_fields = {
        "task",
        "training_seed",
        "stressor",
        "ir_threshold",
        "sr_threshold",
        "base_stressed_score",
        "endpoint_stressed_score",
        "delta_behavior",
        "behavior_class",
        "observed_positive",
        "base_ir_relative",
        "endpoint_ir_relative",
        "base_sr",
        "endpoint_sr",
    }
    fields = set(rows[0])
    missing = sorted(expected_fields - fields)
    if missing:
        raise ValueError(f"canonical source is missing fields: {missing}")
    expected_keys = {
        (task, seed, stressor)
        for task in TASKS
        for seed in SEEDS
        for stressor in STRESSORS
    }
    observed_keys = {
        (row["task"], int(row["training_seed"]), row["stressor"])
        for row in rows
    }
    if observed_keys != expected_keys:
        raise ValueError(
            "canonical coverage mismatch; expected 4 tasks x 3 seeds x 2 stressors"
        )
    for row in rows:
        if row["behavior_class"] not in {"positive", "neutral", "negative"}:
            raise ValueError(f"unexpected behavior label: {row['behavior_class']!r}")
        if not math.isclose(_float(row["base_ir_relative"]), 1.0, abs_tol=1e-10):
            raise ValueError("canonical base IR relative value must be 1")


def build_rows(source_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    _validate_source(source_rows)
    output: list[dict[str, Any]] = []
    for source in source_rows:
        base_ir = _float(source["base_ir_relative"])
        endpoint_ir = _float(source["endpoint_ir_relative"])
        base_sr = _float(source["base_sr"])
        endpoint_sr = _float(source["endpoint_sr"])
        ir_threshold = _float(source["ir_threshold"])
        sr_threshold = _float(source["sr_threshold"])
        endpoint_ir_pass = endpoint_ir <= ir_threshold
        endpoint_sr_pass = endpoint_sr >= sr_threshold
        output.append(
            {
                "task": source["task"],
                "training_seed": int(source["training_seed"]),
                "stressor": source["stressor"],
                "ir_threshold": ir_threshold,
                "sr_threshold": sr_threshold,
                "base_stressed_score": _float(source["base_stressed_score"]),
                "endpoint_stressed_score": _float(source["endpoint_stressed_score"]),
                "delta_behavior": _float(source["delta_behavior"]),
                "behavior_class": source["behavior_class"],
                "observed_positive": _as_bool(source["observed_positive"]),
                "base_ir_relative": base_ir,
                "endpoint_ir_relative": endpoint_ir,
                "ir_improvement": base_ir - endpoint_ir,
                "base_sr": base_sr,
                "endpoint_sr": endpoint_sr,
                "sr_change": endpoint_sr - base_sr,
                "endpoint_ir_pass": endpoint_ir_pass,
                "endpoint_sr_pass": endpoint_sr_pass,
                "ir_pass_sr_reject_veto": endpoint_ir_pass and not endpoint_sr_pass,
            }
        )
    return sorted(
        output,
        key=lambda row: (TASKS.index(row["task"]), row["training_seed"], STRESSORS.index(row["stressor"])),
    )


def build_summary(rows: list[dict[str, Any]], source: Path) -> dict[str, Any]:
    summary = {
        "schema_version": "paper1-cross-stressor-component-analysis-1.0",
        "source": str(source),
        "n_rows": len(rows),
        "tasks": list(TASKS),
        "training_seeds": list(SEEDS),
        "stressors": list(STRESSORS),
        "definitions": {
            "ir_improvement": "1 - endpoint_ir_relative; the canonical base value is 1",
            "sr_change": "endpoint_sr - base_sr",
            "positive_component_change": "A component change greater than zero is counted as positive.",
            "sign_target": "The predefined observed_positive label in the canonical source; behavior_class and delta_behavior are retained per row.",
            "absolute_endpoint_gate": "IR passes when endpoint_ir_relative <= ir_threshold; SR passes when endpoint_sr >= sr_threshold; a veto is an IR-pass/SR-reject endpoint.",
        },
        "sampling_note": "The 24 rows are paired checkpoint/stressor observations, not IID samples. Task summaries contain four task clusters with three seeds per stressor; LOTO ranges omit one task cluster at a time.",
        "cluster_resampling": {
            "definition": "Sensitivity distribution from exact enumeration of all 4^4=256 ordered draws of the four task clusters with replacement. This is not a precise confidence interval for a new-task population.",
            "ir_improvement": _cluster_resampling_for_component(
                rows, "ir_improvement"
            ),
            "sr_change": _cluster_resampling_for_component(rows, "sr_change"),
        },
        "pooled": _scope_metrics(rows),
        "by_task": {
            task: _scope_metrics([row for row in rows if row["task"] == task])
            for task in TASKS
        },
        "by_stressor": {
            stressor: _scope_metrics(
                [row for row in rows if row["stressor"] == stressor]
            )
            for stressor in STRESSORS
        },
        "leave_one_task_out": _loto_metrics(rows),
    }
    return _json_ready(summary)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "--"
    return f"{float(value):.{digits}f}"


def _scope_table_row(
    label: str, metrics: dict[str, Any], cluster_cell: str = "--"
) -> str:
    ir = metrics["ir_improvement"]
    sr = metrics["sr_change"]
    gate = metrics["absolute_endpoint_gate"]
    return (
        f"{label} & {metrics['n']} & "
        f"{_fmt(ir['spearman_delta_behavior'])} & {_fmt(sr['spearman_delta_behavior'])} & "
        f"{_fmt(ir['sign_agreement'])} / {_fmt(sr['sign_agreement'])} & "
        f"{gate['endpoint_ir_pass_n']} / {gate['ir_pass_sr_reject_veto_n']} & "
        f"{cluster_cell} \\\\"
    )


def write_summary_table(summary: dict[str, Any], path: Path) -> None:
    lines = [
        r"\begin{table}[H]",
        r"\centering",
        r"\caption{Descriptive cross-stressor component summary. IR improvement is $1-\mathrm{IR}_{\rm rel}$ because the base value is 1; SR change is endpoint SR minus base SR. Spearman values correlate each component change with planning-success change. Binary agreement compares a positive component change with the prespecified positive behavior label. ``IR pass / veto'' reports absolute endpoint IR passes and the subset rejected by SR. The final cell gives the 2.5th--97.5th percentiles from exact enumeration of all $4^4=256$ ordered task-cluster resamples, using linear interpolation. This is a sensitivity distribution, not a new-task population CI; the 24 paired rows are not IID.}",
        r"\label{tab:cross-stressor-components-v1}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{lrrrrrl}",
        r"\toprule",
        r"Scope & $n$ & $\rho_{\rm IR}$ & $\rho_{\rm SR}$ & \shortstack{binary agreement\\IR / SR} & IR pass / veto & \shortstack{cluster-resampling\\sensitivity} \\",
        r"\midrule",
        _scope_table_row(
            "Pooled",
            summary["pooled"],
            (
                r"\shortstack{IR: ["
                + _fmt(summary["cluster_resampling"]["ir_improvement"]["p2_5"])
                + ", "
                + _fmt(summary["cluster_resampling"]["ir_improvement"]["p97_5"])
                + r"]\\SR: ["
                + _fmt(summary["cluster_resampling"]["sr_change"]["p2_5"])
                + ", "
                + _fmt(summary["cluster_resampling"]["sr_change"]["p97_5"])
                + r"]}"
            ),
        ),
        _scope_table_row("Blur", summary["by_stressor"]["blur"]),
        _scope_table_row("Resize", summary["by_stressor"]["resize"]),
        r"\midrule",
    ]
    for task in TASKS:
        lines.append(_scope_table_row(task, summary["by_task"][task]))
    loto = summary["leave_one_task_out"]["spearman_range"]
    lines.extend(
        [
            r"\midrule",
            f"LOTO range & 18 & [{_fmt(loto['ir_improvement'][0])}, {_fmt(loto['ir_improvement'][1])}] & [{_fmt(loto['sr_change'][0])}, {_fmt(loto['sr_change'][1])}] & -- & -- & -- \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_appendix_table(rows: list[dict[str, Any]], path: Path) -> None:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Descriptive per-pair component values for all 24 canonical blur/resize endpoints. IR improvement is $1-\mathrm{IR}_{\rm rel}$ and SR change is endpoint SR minus base SR, so positive values have the same improvement interpretation across panels. ``IR pass'' uses the fixed absolute endpoint threshold; ``veto'' marks an IR-pass/SR-reject endpoint. The rows are paired observations with task clustering and are not IID replicates.}",
        r"\label{tab:cross-stressor-components-all-pairs-v1}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{lrlrrrrrrl}",
        r"\toprule",
        r"Task & Seed & Shift & $\Delta P$ & Label & IR$_{\rm rel}$ & IR imp. & SR change & IR pass / veto \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['task']} & {row['training_seed']} & {STRESSOR_LABELS[row['stressor']]} & "
            f"{row['delta_behavior']:.1f} & {row['behavior_class']} & "
            f"{row['endpoint_ir_relative']:.3f} & {row['ir_improvement']:.3f} & "
            f"{row['sr_change']:.3f} & "
            f"{'yes' if row['endpoint_ir_pass'] else 'no'} / "
            f"{'yes' if row['ir_pass_sr_reject_veto'] else 'no'} \\\\" 
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table*}"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _cell(rows: list[dict[str, Any]], task: str, stressor: str) -> list[dict[str, Any]]:
    cell = [row for row in rows if row["task"] == task and row["stressor"] == stressor]
    if len(cell) != len(SEEDS):
        raise ValueError(f"{task}/{stressor}: expected {len(SEEDS)} seeds, found {len(cell)}")
    return sorted(cell, key=lambda row: row["training_seed"])


def _draw_panel(
    axis: Any,
    rows: list[dict[str, Any]],
    value_key: str,
    ylabel: str,
    title: str,
    value_digits: int,
    show_points: bool = True,
) -> None:
    positions: list[float] = []
    means: list[float] = []
    for task_index, task in enumerate(TASKS):
        group_start = task_index * 3.0
        for stressor_index, stressor in enumerate(STRESSORS):
            cell = _cell(rows, task, stressor)
            values = [float(row[value_key]) for row in cell]
            position = group_start + stressor_index
            positions.append(position)
            means.append(mean(values))
            axis.bar(
                position,
                mean(values),
                width=0.82,
                color=STRESSOR_COLORS[stressor],
                hatch="///" if stressor == "resize" else None,
                edgecolor="#333333" if stressor == "resize" else STRESSOR_COLORS[stressor],
                linewidth=0.35,
                alpha=0.88,
                zorder=2,
            )
            # The three points make the seed-level spread visible without
            # treating seeds as independent task-level replicates.
            offsets = (-0.18, 0.0, 0.18)
            for offset, value in zip(offsets, values) if show_points else ():
                axis.scatter(
                    position + offset,
                    value,
                    s=12,
                    color="#222222",
                    edgecolors="white",
                    linewidths=0.35,
                    zorder=4,
                )
    axis.axhline(0.0, color="#222222", linewidth=0.9, zorder=3)
    ymin = min([0.0, *[float(row[value_key]) for row in rows]])
    ymax = max([0.0, *[float(row[value_key]) for row in rows]])
    span = max(ymax - ymin, 1e-6)
    axis.set_ylim(ymin - 0.12 * span, ymax + 0.16 * span)
    axis.set_xticks([task_index * 3.0 + 0.5 for task_index in range(len(TASKS))])
    axis.set_xticklabels([TASK_LABELS[task] for task in TASKS])
    axis.tick_params(axis="x", length=0)
    axis.set_xlim(-0.75, (len(TASKS) - 1) * 3.0 + 1.75)
    axis.set_ylabel(ylabel)
    axis.set_title(title, loc="left", fontweight="semibold")
    axis.grid(True, axis="y", color="#A0A0A0", alpha=0.25, linewidth=0.5)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def plot(rows: list[dict[str, Any]], pdf_path: Path, png_path: Path, *, show_points: bool = True) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(PLOT_STYLE):
        figure, axes = plt.subplots(1, 3, figsize=(7.25, 2.55), sharex=False)
        _draw_panel(
            axes[0],
            rows,
            "delta_behavior",
            "Planning success change (pp)",
            "(a) Planning outcome",
            1,
            show_points=show_points,
        )
        _draw_panel(
            axes[1],
            rows,
            "ir_improvement",
            "IR improvement",
            "(b) IR component",
            2,
            show_points=show_points,
        )
        _draw_panel(
            axes[2],
            rows,
            "sr_change",
            "SR change",
            "(c) SR component",
            2,
            show_points=show_points,
        )
        legend_handles = [
            Patch(facecolor=STRESSOR_COLORS["blur"], label="Blur"),
            Patch(
                facecolor=STRESSOR_COLORS["resize"],
                edgecolor="#333333",
                hatch="///",
                label="Resize",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                linestyle="None",
                color="#222222",
                markerfacecolor="#222222",
                markeredgecolor="white",
                markersize=4,
                label="one point per seed",
            ),
        ]
        figure.legend(
            handles=legend_handles if show_points else legend_handles[:2],
            loc="upper center",
            bbox_to_anchor=(0.5, 1.03),
            ncol=3 if show_points else 2,
            frameon=False,
            handlelength=1.4,
            columnspacing=1.1,
            handletextpad=0.4,
        )
        figure.text(
            0.5,
            0.005,
            "Positive values indicate improvement; bars are means over three seeds.",
            ha="center",
            va="bottom",
            fontsize=6.8,
            color="#444444",
        )
        figure.subplots_adjust(left=0.065, right=0.995, bottom=0.21, top=0.78, wspace=0.40)
        figure.savefig(pdf_path)
        figure.savefig(png_path, dpi=240)
        plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--rows-out", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--summary-out", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--table-out", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--appendix-out", type=Path, default=DEFAULT_APPENDIX)
    parser.add_argument("--figure-out", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--figure-png-out", type=Path, default=DEFAULT_FIGURE_PNG)
    args = parser.parse_args()

    source_rows = _read_csv(args.source)
    rows = build_rows(source_rows)
    summary = build_summary(rows, args.source)
    _write_csv(args.rows_out, rows)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_summary_table(summary, args.table_out)
    write_appendix_table(rows, args.appendix_out)
    plot(rows, args.figure_out, args.figure_png_out)
    print(f"wrote {args.rows_out} ({len(rows)} rows)")
    print(f"wrote {args.summary_out}")
    print(f"wrote {args.table_out}")
    print(f"wrote {args.appendix_out}")
    print(f"wrote {args.figure_out}")
    print(f"wrote {args.figure_png_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
