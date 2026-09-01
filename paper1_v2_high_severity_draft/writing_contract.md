# Writing contract

## Submission frame

- Target: ICLR/NeurIPS main conference, read as a diagnostic and empirical-analysis paper.
- Paper type: diagnostic study with supporting samplewise analysis, not a new
  training objective or planner.
- Central thesis: action-conditioned rollout comparisons expose how visual
  perturbations propagate through a world model; IR measures same-history
  sensitivity and SR checks whether the tested state distinctions survive that
  contraction.
- Claim frame: **This is a diagnostic study of rollout sensitivity and tested
  state separation, not a universal robustness certificate or a checkpoint
  selector.**
- Reader promise: after the new subsection, a first-time reader should
  understand why SR can be nonbinding in the original moderate regime yet
  become active in a broader severity regime without any contradiction.
- Abstract revision rule: preserve the concise v1 abstract because the new
  experiment strengthens an existing claim rather than changing the central
  contribution or strongest headline result.

## Allowed claims

1. The broad-severity experiment is separate from the original narrow sweep.
2. It contains 96 trained LeWM checkpoints: four tasks, eight training-noise
   ranges, and three independent training runs; each is evaluated at four noise
   severities.
3. The H=8 diagnostic protocol, pair construction, and IR/SR thresholds are
   unchanged in the extension.
4. At evaluation noise 0.08 and 0.16, SR changes 3 of 96 IR-passing decisions
   at each severity; at 0.32 and 0.64 it changes 10 of 82 and 11 of 46,
   respectively. The low-severity events are the same three extreme-training
   TwoRoom checkpoints, not rows from the original narrow training grid.
5. Lower relative IR and higher SR have positive descriptive rank associations
   with same-checkpoint robustness retention after additive design trends are
   removed. These associations remain positive after rank adjustment for the
   simple train--evaluation exposure ratio. Small differences among their
   direct correlations are not evidence of superiority over metadata.
6. The evidence supports a regime-dependent guard role for SR.

## Disallowed claims

- A best, optimal, or selected training-noise maximum.
- A post-hoc robustness band or a newly tuned high-severity label.
- Selector superiority, prospective checkpoint selection, or improved planning.
- Universal robustness, causal effects of SR, or a sufficient condition for
  downstream success.
- Superiority over all training metadata; the exposure ratio is one simple
  comparator only.
- A homogeneous 17-level training sweep obtained by concatenating the old and
  new grids.
- Treating 384 diagnostic rows, 96 checkpoints, evaluation seeds, or factorial
  cells as independent population replicates.

## Evidence map

| Claim | Evidence | Paper role |
|---|---|---|
| SR is nonbinding in the original moderate sweep | 77 IR-passing rows, all 77 pass SR | Existing main result |
| Low IR alone admits a constant representation | Definition-level counterexample; SR requires tested state separation | Conceptual motivation, not an empirical claim |
| SR becomes more active in broader evaluated-severity slices | Fixed-threshold decision decomposition over 384 rows | New main display |
| IR and SR vary with robustness retention beyond a simple exposure ratio | Within-task/run factorial associations, aggregated by run then task | New main prose; exact table in appendix |
| Diagnostics do not replace nominal quality evaluation | Same-checkpoint retention definition and observed nominal failures | Boundary claim |

## Main-text budget

- One new subsection of roughly 300--400 words.
- One simple main figure with no task heatmaps and no rank-correlation panel.
- No new acronym.
- Exact association ranges and sensitivity outcome remain in the appendix.
- Replace obsolete future-work and threshold-edge sentences rather than merely
  appending more caveats.

## Quality gates adopted from CairnLab

- G1 progressive disclosure; G3 one job per paragraph/display.
- G4 claim/evidence identity and explicit aggregation.
- G5 verbs matched to descriptive evidence.
- G6 self-contained, grayscale-readable display.
- G7 one comparison grammar per table.
- G8 manuscript/provenance separation.
- G9 single source of truth for every number.
- G10 fresh-reader and compiled-PDF review.
- Claim compression, subtractive remediation, and diagnostic-paper score calibration.

The CairnLab claim-lifecycle governance model is not imported. It is unrelated
to the scientific content and release process of this repository.

## Acceptance checks

- `paper1/main.tex` remains unchanged during drafting.
- Every draft number is generated from the frozen three-seed summary.
- The preview compiles twice with TeX Live 2025 and has no unresolved references.
- A first-time reader can explain the moderate-regime/high-severity relationship
  from the figure and caption without reading the appendix.
- The text never implies selector utility or a best training strength.
- The abstract remains identical to v1 apart from mechanically shared metadata.
