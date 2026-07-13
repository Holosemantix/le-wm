# Paper1 ACPC Scientific Remediation Plan — 2026-07-13

This is the durable continuation of the submission-facing remediation handoff.
It records the corrected scientific reading and the binding scope for the next
pass so that later sessions do not restart the review.

## Binding editorial rule

Restore only theory, evidence, figures, and tables that directly strengthen the
central claim:

> Action-matched long-horizon ACPC provides target-free information about
> future prediction drift beyond encoder/H1 and action- or time-destroyed
> controls, and this information is relevant to planner decision stability.

Do not restore material merely to increase length. Old exploratory failures,
weak side branches, redundant sweeps, audit history, and theory without a
non-vacuous empirical counterpart remain outside the manuscript.

Formal prospective experiments are different: once a new protocol is frozen,
all valid outcomes, including failures, must be reported and the claim must be
adjusted if a gate fails.

## Corrected evidence reading

The main baseline comparison is P1, the held-out action-matched future-drift
estimand. On primary seeds 3073/3074, correct-action ACPC-H8 gives:

- 56.5% lower absolute-drift MAE than H1, with conditional 95% cluster
  bootstrap interval [51.1%, 61.2%];
- 51.9% lower absolute-drift MAE than the strongest action/time-destroyed H8
  control, with interval [45.0%, 56.6%];
- 55.5% and 50.6% reductions for adverse drift;
- wins against H1 and every destroyed-H8 control in 57/64 seed-averaged
  task-by-trajectory clusters; and
- a separate pass on all four tasks in each primary seed, including the fully
  protocol-frozen seed3074 replication.

These results support an ACPC advantage. The paper and reviewer-risk assessment
must not characterize the main result as being matched by a simple baseline.

The 24-pair blur/resize component table measures a different checkpoint-change
association estimand. Its mixed metrics do not identify a statistically valid
ranking among components, so it cannot negate P1 and should not be described as
baseline catch-up. Remove the component-ranking table from the manuscript if it
does not support a precise claim; retain its generator and artifact for
reproducibility. P3 remains transfer evidence, while P1 is the action/horizon
specificity test.

## Claim hierarchy

1. Central claim: correct-action ACPC-H8 adds large held-out future-drift
   information beyond encoder/H1 and structure-destroyed controls.
2. Strong supporting claim: ACPC-induced rollout/cost drift plus clean planner
   margins predicts or certifies stability of actual CEM decisions under a
   frozen protocol.
3. Supporting scope: LeWM family-local calibration transfers across held-out
   training seeds, and a paired score retains ordering under fixed blur/resize
   without stressor-specific refitting.

SMPR remains a gross-collapse guard, not a co-equal contribution. P3 must not
dilute the ACPC mechanism claim.

## Theory to restore

### Main text

The visible main-text theory must be stronger than the current reverse-triangle
statement. Keep that future-error-drift theorem and add one compact
planner-linked chain:

1. Under a locally Lipschitz cost readout, ACPC bounds candidate-cost drift.
2. If paired candidate-cost drift is smaller than the clean top-1 or
   elite-boundary margin, the selected candidate or elite set is preserved.
3. Under deterministic CEM updates and common random numbers, preserved elite
   membership and ordering preserve the next proposal; induction across rounds
   preserves the final first action.

The main text should state the three levels explicitly:

future-error drift -> candidate-cost drift -> adaptive-CEM decision.

The first result is samplewise, the second is margin conditional, and the third
is conditional on common proposals and deterministic updates. It is not a
universal closed-loop guarantee.

### Appendix

Put complete assumptions and proofs in the appendix:

- the reverse-triangle bound in weighted projected-rollout space;
- the Lipschitz candidate-cost lemma;
- candidate-wise sharp top-1 and elite-boundary conditions;
- the deterministic adaptive-CEM induction/corollary;
- tie handling and common-random-number scope;
- the boundary between one planning call and repeated closed-loop replanning;
- the empirical statistic corresponding to each theoretical object.

### Theory not to restore

- the numerically vacuous sampled-pool K-times-alpha union bound;
- repeated pseudo-metric or triangle-inequality lemmas;
- long local-linearization/JVP derivations or heatmaps;
- claims that substitute checkpoint q90 ATR for a uniform candidate-pool
  certificate;
- closed-loop guarantees unsupported by a closed-loop experiment.

The existing local-sensitivity figure is optional and should yield its space to
the planner-linked result. It must not remain just to make the paper longer.

## Strong evidence to add or promote

### Prospective P1 replication

Freeze the protocol before training and add at least one new fully prospective
four-task model seed, provisionally seed3075. If compute allows, pre-register
seed3075 and seed3076 and report both.

Keep provenance roles separate:

- seed3074: existing fully frozen replication;
- new seed or seeds: prospective replications;
- seed3073: development-support result in the existing primary estimate;
- seed3072: retrospective completeness check, never relabeled as confirmatory.

Predeclare a pass rule before observing new results: correct H8 must beat H1
and every destroyed-H8 control; the equal-task improvement must exceed a fixed
practical threshold; at least three of four tasks must pass; leave-one-task-out
aggregation must not reverse the result; all valid results must be reported.

### Actual planner-decision closure

The existing operational code and smoke artifacts are feasibility work. Create
a new versioned protocol/addendum rather than mutating frozen v1 hashes.

Run two nested formal panels:

1. A 64- or 100-block shared-candidate panel estimating top-1/elite event rates
   with useful uncertainty.
2. A frozen adaptive-CEM panel on all four tasks, beginning with seed3074
   base/endpoint checkpoints and then the new prospective seed.

Primary metrics:

- first-action RMS deviation and stability at a frozen tolerance;
- full-plan RMS deviation;
- elite-set Jaccard and elite-boundary preservation;
- selected-decision regret under clean cost;
- theorem-condition coverage and conditional failure rate;
- compute and memory overhead.

Gaussian perturbation is primary. Blur/resize may be a compact transfer slice
after the primary panel passes. The purpose is to close planning relevance, not
to repeat the P1 baseline contest.

### Existing P1 evidence presentation

- Correct the setup paragraph so logged-H8 and candidate-H5 covariates are not
  conflated.
- Expand ACPC and ATR on first use and define all target/control responses.
- Report absolute MAE for H1, best destroyed H8, and correct H8 in the
  appendix.
- Preserve relative improvements in the main result.
- Show task- and seed-level points rather than only one pooled percentage.
- State provenance and conditional training-seed uncertainty once, clearly.
- Keep seed3072 retrospective and separate.

## Strong figures and tables

### Main figures

1. New vector method figure: same-state nominal/corrupted views, shared action
   sequence, rollout divergence, future-error bound, and planner-margin link.
   Redraw the old intuitive raster in current notation.
2. Keep the four-task full-sweep figure. Clarify that plotted ATR is normalized
   for visualization while the gate uses canonical raw ATR, and state the
   exact recovery rule.
3. New P1 advantage forest/dot plot: correct H8 versus H1 and the strongest
   destroyed H8 by task and seed, with pooled conditional uncertainty.
4. New planner-stability figure: first-action/elite stability versus the frozen
   ACPC-plus-margin condition, including uncertainty and failures.
5. Keep the P3 scatter only if space remains after the four jobs above;
   otherwise move it to the appendix.

### Appendix figure

Keep the qualitative t-SNE figure. It is intuitive but not metric preserving:
no t-SNE distance, area, or overlap enters a quantitative claim, and ATR/SMPR
remain computed in the original rollout space.

### Tables

- Main P1 table: relative improvement with four-task visibility and both
  comparator classes.
- Appendix P1 table: absolute MAEs, task/seed cells, sample units, and exact
  controls.
- Compact four-row full-sweep summary: base stressed loss, recovered
  performance, and recovery-region coverage.
- Keep compact P2/P3 summary tables but make them visually subordinate to P1.
- Do not restore the 36-row sweep dump or the cross-stressor component-ranking
  table.

All displays require final-size readable fonts, consistent task encodings,
explicit uncertainty semantics, aggregation units, and a clear non-claim
boundary in each caption.

## Content that remains deleted

- the 36-row raw full sweep and redundant endpoint/sweep figures;
- weak one-family PLDM material;
- the failed repair experiment;
- the candidate-H5 result as a four-task claim;
- proxy-negative and sensitivity audit history;
- duplicate fixed-pool and JVP tables;
- concurrent-work bookkeeping tables;
- internal remediation, manifest, or lockbox prose.

## Missing definitions to repair

- expand the ACPC and ATR names on first use;
- state the exact 80%-recovery and at-most-5pp-clean-drop rule;
- report frozen thresholds and the lexicographic calibration rule in the
  appendix;
- distinguish logged-H8 and candidate-H5 covariates and estimands;
- clarify full-sweep ATR normalization;
- remove duplicated experimental prose;
- modestly restore closest-work comparison only where it sharpens novelty.

## Execution order

1. Freeze, commit, and push a new protocol/addendum to both remotes.
2. Repair/version operational code against that protocol and run tests.
3. Run adaptive-CEM evaluation on existing frozen checkpoints while the new
   prospective model seed trains.
4. Summarize without changing gates.
5. Integrate only evidence that directly supports the claim hierarchy.
6. Rebuild theory, figures, tables, normal/blind PDFs, and consistency checks.
7. Commit the explicit Paper1 scope and push both remotes.

If a formal new result fails, report it and reduce the associated claim. Do not
replace a prospective seed or silently redefine a gate after outcomes.

## Page allocation and reviewer forecast

The 14-page compressed draft is not wrong because it is short; its remaining
problem is allocation. A likely 16--17 page total is appropriate if the added
pages are planner-linked theory, absolute P1 evidence, a compact sweep summary,
and formal planner results. No weak side branch returns to fill pages.

Current reviewer estimate remains about 6/10. Writing-only restoration may add
at most about 0.5. A passing prospective P1 seed plus a prospectively frozen
adaptive-CEM result is the highest-value path toward roughly 7/10.

## Progress

- [x] Submission-facing compression, visual cleanup, tests, blind build, and
  publication to both remotes completed.
- [x] Seed3072 four-task retrospective P1 check completed separately.
- [x] Corrected the interpretation: P1 shows a large ACPC advantage; a
  different cross-stressor component estimand is not baseline catch-up.
- [x] Fixed the restore boundary to strong theory, strong evidence, and
  claim-bearing figures/tables only.
- [x] Freeze the new scientific protocols and executable manifests.
- [ ] Commit and publish the frozen pre-result state to both remotes.
- [ ] Run prospective P1 replication.
- [ ] Run formal shared-pool and adaptive-CEM evaluation.
- [ ] Integrate passing evidence and rebuild the submission.
