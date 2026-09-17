"""Read-only reproduction of the appendix recovery-fraction sensitivity table.

Run: python -m paper1.scripts.check_recovery_fraction_sensitivity
Uses the original diagnostics, not the separate zero-scale-anchor ablation.
"""
import json

from .utils_paper1_io import ROOT, label_rows, read_csv
from .cross_task_selective_rule import run_all_subsets


def main():
    rows = read_csv(ROOT / 'paper1/results/full_sweep_diagnostics.csv')
    original = json.loads((ROOT / 'paper1/results/cross_task_ir_sr_all_subsets_summary_v2.json').read_text())
    result = []
    for fraction in (0.7, 0.8, 0.9):
        labeled = label_rows([dict(row) for row in rows], recovery_fraction=fraction, clean_tolerance=5.0)
        if fraction == 0.8:
            key = lambda row: (row['task'], str(row['training_seed']), float(row['rho']))
            assert {key(r): r['recovery_label'] for r in rows} == {key(r): r['recovery_label'] for r in labeled}
        details, params, summary = run_all_subsets(labeled)
        for coverage in summary['coverage']:
            subset = [r for r in details if r['source_coverage'] == coverage['source_coverage']]
            missing = [r for r in subset if r['predicted_start'] is None or r['behavioral_start'] is None]
            if fraction == 0.8:
                old = next(r for r in original['coverage'] if r['source_coverage'] == coverage['source_coverage'])
                for metric in ('balanced_accuracy', 'precision', 'recall', 'mean_abs_start_error', 'max_abs_start_error'):
                    assert abs(coverage[metric] - old[metric]) < 1e-12
            result.append(dict(
                recovery_fraction=fraction,
                source_tasks=coverage['source_coverage'],
                balanced_accuracy=coverage['balanced_accuracy'],
                precision=coverage['precision'], recall=coverage['recall'],
                mean_onset_grid_error=None if missing else coverage['mean_abs_start_error']/0.01,
                max_onset_grid_error=None if missing else coverage['max_abs_start_error']/0.01,
                no_selection=sum(r['predicted_start'] is None for r in subset),
                missing_onset_cases=[{k: r[k] for k in ('source_tasks', 'task', 'training_seed', 'behavioral_start', 'predicted_start')} for r in missing],
                selected_threshold_counts=coverage['selected_threshold_counts'],
            ))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
