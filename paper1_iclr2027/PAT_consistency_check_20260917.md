# PAT revision consistency check — 2026-09-17

Scope: approved edits in `main.tex`, associated tables, Figure 2, and feasibility of remaining follow-ups. This is not a new independent validation of all experiments. No original experimental results were replaced.

## Checks completed

- Final TeX Live 2025 build after adding Table 13: 25 PDF pages, nine main-text pages, 44 bibliography entries. Final LaTeX log has no undefined-reference/citation or overfull-box warnings. Distributed and build PDFs match.
- Recovery-criterion sensitivity was recomputed with `PYTHONPATH=. python -m paper1.scripts.check_recovery_fraction_sensitivity`. Its assertions preserve the original 0.8 labels and metrics. All nine rounded balanced accuracies match Table 10:

| Recovery fraction | One source task | Two source tasks | Three source tasks |
|---|---:|---:|---:|
| 0.7 | 0.854 | 0.895 | 0.895 |
| 0.8 | 0.855 | 0.900 | 0.900 |
| 0.9 | 0.779 | 0.799 | 0.813 |

- Exactly one no-selection case occurs at fraction 0.9 with one source task; it remains included in classification evaluation.
- Appendix C's zero-scale sensitivity retains the original metric. Rechecking the 27 PushT rows gives maximum absolute relative-IR change 0.033556 and one crossing at each of IR thresholds 0.1 and 0.3. This is not a claim that all threshold decisions are unchanged.
- Figure 2's added diagnostic error bars span the three runs (minimum to maximum), not standard errors or confidence intervals. The caption uses the same convention.
- New table labels resolve; LOTO and quantile abbreviations are explained. Regression standardization is fitted on source tasks, with no target standardization beyond log1p.
- An independent Claude Code / GLM text-and-code check corroborated threshold-selection and labeling consistency. Its concern about missing stored sensitivity output was addressed by rerunning the script and recording the rounded results above. An obsolete section title in a plotting-script comment was corrected.

## Earlier feasibility findings (superseded by final decisions below)

- Control5: the second independent Claude Code / GLM check found no destroyed-action features in the original CEM panel. Scalar features and pool hashes are stored, not candidate action tensors. Candidate pools must be regenerated and checked, then new control rollouts computed. Cached adaptive outcomes can only be reused with matching row keys and the same protocol. Existing legacy and later H5 analyses must not be combined blindly: `reviewer_cem_analysis.py` records a history-versus-future index distinction. This remains a substantive prerequisite, not a resolved formatting matter. No new experiment was launched.
- Target-scale summaries: sample-level prediction-error and CEM-regret records exist. The second worker was uncertain about persistence of prediction-error targets; the primary review found `correct_absolute_h8_error_drift` in `paper1/results/reviewer_strengthening_20260907/logged_endpoint/replayed_logged_rows_12cells.csv`. Original CEM targets are in the adaptive shards used by `summarize_acpc_planner_three_seed.py`. Summaries can be computed without model training; exact sample filters and task/run grouping must match the reported regressions.
- Dynamic visual benchmarks: consider one contextual citation sentence, not a new benchmark experiment.
- Targeted attacks: consider only a brief scope clarification; do not imply adversarial safety was evaluated.
- Appendix C currently says Gaussian-noise experiments use sigma=0.08 without qualifying the main sweep. A minimal qualifier would distinguish it from the additional severity experiments; wording awaits author approval.

## Final author-approved disposition

- Added Table 13 in Appendix I: target-value means and sample standard deviations, using the same nonzero-perturbation samples and target scales as the regressions. Caption distinguishes target variation from uncertainty in the mean. Numerical check: `python -m paper1.scripts.check_regression_target_scales`.
- Qualified the sigma=0.08 statement with an automatic reference to Section 4.2.
- No additional DCS/DMC-GB background sentence or references.
- No targeted-attack experiment or additional manuscript paragraph.
- Control5 was subsequently computed on the separate true-H5 experiment (24 model combinations; 7,200 regression rows), with correct-feature and candidate-pool reproduction checks. It did not show an advantage of original actions over time-shuffled controls. The author chose not to add this follow-up to the manuscript. This does not resolve the previously recorded legacy CEM interpretation issue or authorize altering original results.
- Manuscript prose was approved item by item. Control5 follow-up outputs remain separate from the paper changes being submitted to Git.
