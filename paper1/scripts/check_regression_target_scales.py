"""Read-only descriptive target scales for a proposed appendix table.

No regression refitting or manuscript edits. SD describes pooled target values,
not uncertainty of an estimated mean; repeated observations are not independent.
Run: python -m paper1.scripts.check_regression_target_scales
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    ("prediction_error_drift", "logged_endpoint/replayed_logged_rows_12cells.csv",
     "correct_absolute_h8_error_drift", False, 96),
    ("log1p_selection_regret", "cem/design_rows_legacy.csv",
     "positive_clean_regret", True, 600),
)


def summarize():
    output = []
    for name, relative_path, field, use_log, expected_n in SOURCES:
        source = ROOT / "paper1/results/reviewer_strengthening_20260907" / relative_path
        groups = defaultdict(list)
        with source.open(newline="") as stream:
            for row in csv.DictReader(stream):
                if float(row["severity"]) <= 0:
                    continue
                value = float(row[field])
                assert np.isfinite(value) and value >= 0, (name, row)
                groups[(row["task"], int(row["training_seed"]))].append(
                    float(np.log1p(value)) if use_log else value
                )
        tasks = ("TwoRoom", "PushT", "Reacher", "Cube")
        seeds = (3072, 3073, 3074)
        assert set(groups) == {(task, seed) for task in tasks for seed in seeds}
        assert all(len(values) == expected_n for values in groups.values())
        for task in tasks:
            runs = [np.asarray(groups[(task, seed)]) for seed in seeds]
            values = np.concatenate(runs)
            output.append({
                "target": name, "task": task,
                "source": str(source.relative_to(ROOT)),
                "n_per_run": expected_n, "n_total": len(values),
                "mean": float(values.mean()),
                "target_value_sample_sd": float(values.std(ddof=1)),
                "zero_fraction": float((values == 0).mean()),
                "per_run_means": {str(seed): float(run.mean())
                                  for seed, run in zip(seeds, runs)},
            })
    return output


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, allow_nan=False))
