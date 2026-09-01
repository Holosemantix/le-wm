# Writing-quality review ledger

## Readiness

**Status: ready** for author review as an isolated v2 candidate. This status
does not authorize integration into `paper1/main.tex` and does not reassess the
rest of the paper.

The proposed extension has one defensible paper-facing job: show that the fixed
SR condition is largely inactive in the original moderate regime but becomes
active for more demanding evaluation slices, while continuous IR and SR remain
descriptively associated with same-checkpoint planning retention beyond
additive design trends and a simple exposure ratio.

## Evidence and provenance

- Frozen summary SHA-256:
  `8cbed858644ce3cf4502cce88118a01d976b093b57ffc49307bdc8c33c035505`.
- Frozen joined-row SHA-256:
  `1dd4f2a7d2efe493dc3bdbdea6d7baa6272993d5fc703b00e70ef8fd67b60d27`.
- `scripts/build_draft_assets.py` checks both hashes and the design, threshold,
  and no-retuning assertions before emitting any paper asset.
- Figure, table, prose-number macros, and their hashes are recorded in
  `source_map.json`.
- Two consecutive asset builds produced identical hashes.

## Independent-reader findings addressed

1. **Matched-severity reconciliation.** The three SR failures at evaluation
   noise 0.08 and 0.16 are the same three TwoRoom checkpoints trained at the
   new extreme training levels (one at 1.0, two at 1.5). They are not part of
   the original narrow grid. The main text now says this explicitly.
2. **Concentration of SR failures.** The appendix now reports the task
   distribution: at evaluation noise 0.32 the failures are 4 TwoRoom, 5 PushT,
   and 1 Reacher; at 0.64 they are 5 TwoRoom and 6 PushT. Cube contributes
   none. This prevents the aggregate count from implying uniform coverage.
3. **Conditional denominators.** Figure annotations now show both counts and
   rates among IR-passing rows: 3/96 (3%), 3/96 (3%), 10/82 (12%), and 11/46
   (24%). The caption states that the population changes with severity and that
   the display is not a checkpoint-selection evaluation.
4. **Metadata comparison.** Direct associations are described as similar in
   magnitude, not as a win over exposure metadata. The text emphasizes the
   positive exposure-adjusted associations and explicitly blocks a superiority
   interpretation.
5. **Factorial dependence.** The appendix names the 21 interaction degrees of
   freedom and the row/column constraints induced by double-centering. It does
   not attach row-level inference to 384 dependent rows.
6. **Retention-ratio floor effect.** Percentage-point retention remains the
   primary outcome. The ratio is only a sensitivity check, with the minimum
   clean success and low-denominator caveat stated.
7. **Threshold-grid boundary.** The integration plan now retains the v1
   limitation that 0.3 is the largest tested IR threshold. Broader training and
   evaluation severities do not resolve that separate threshold-grid issue.
8. **Forced-collapse evidence removed.** The v2 candidate deletes the
   controlled SIGReg-collapse result and appendix table. The constant-
   representation failure remains as a definition-level motivation, while the
   empirical SR claim now rests on the separate broad-severity experiment.
9. **Single-point optimum language removed.** The inherited compact sweep table
   now reports the prespecified recovery ranges and no longer identifies a
   highest-success training strength. The original recovery-label protocol is
   unchanged.
10. **Final scope calibration.** A separate read-only review replaced selector-like
    wording with the conditional SR-veto fraction, limited separation claims to
    the tested state-coordinate pairs, disclosed recurring checkpoint rows
    across severity bars, and stated the rank-residualization procedure exactly.
11. **Abstract regression reverted exactly to v1.** The first v2 draft replaced
    the concise evidence ladder at the end of the accepted abstract with
    factorial-analysis details, threshold behavior, an exposure adjustment, and
    defensive scope language. Those statements were accurate but supporting:
    they did not change the central contribution or strongest headline result.
    Their inclusion flattened the contribution hierarchy, raised new reviewer
    expectations, and replaced the scientific takeaway with analysis plumbing.
    After the author requested a v1 reversion, the complete abstract was restored
    verbatim and checked against `paper1/main.tex` with a source diff.

## CairnLab gates adopted

| Gate | Status | Evidence in this package |
|---|---|---|
| G1. Progressive Disclosure | Pass | Main subsection moves from the moderate-regime question to one display, continuous association, and a boundary statement. |
| G2. Concrete Before Abstract | Pass | Fixed-threshold events are shown before the factorial association analysis; IR and SR retain their definitions from the preceding paper section. |
| G3. One Job | Pass | Main figure shows only condition activation; exact associations and sensitivity remain in the appendix. |
| G4. Claim--Evidence Identity | Pass | Design, training runs, row unit, thresholds, aggregation, task ranges, and dependence are stated; claims remain descriptive. |
| G5. Conceptual and Statistical Precision | Pass | Diagnostic activity, behavioral association, nominal quality, and checkpoint selection are explicitly separated. |
| G6. Self-Contained Display | Pass | Caption gives unit, denominator, conditions, aggregation boundary, and non-selection interpretation; hatches make the figure grayscale-readable. |
| G7. Table Semantics | Pass | The appendix table uses one association grammar, with direct and exposure-adjusted columns and task ranges labeled as non-CIs. |
| G8. Public-Manuscript Boundary | Pass | Hashes, paths, compatibility history, and build notes stay in repository documents rather than manuscript prose. |
| G9. Single Source of Truth | Pass | Generated macros supply all result numbers; source hashes are pinned and regeneration is deterministic. |
| G10. Reader-Test Review | Pass | An unfamiliar-reader review was applied; both the isolated preview and the full 29-page manuscript were inspected at normal zoom and built with TeX Live 2025 with no unresolved references or layout warnings. |

The CairnLab claim-lifecycle and release-governance rules were not imported;
they do not match this repository's authority model. Their writing contract,
claim compression, display accessibility, provenance separation, subtractive
remediation, and compiled-reader checks were adopted because they directly
improve this manuscript task.

## Remove, merge, or demote

- Remove the old high-severity heatmap/rank-correlation composite from the v2
  proposal; the stacked bar has a single reader-facing job.
- Remove the forced SIGReg-collapse paragraph and appendix table; do not retain
  their numerical results elsewhere in the manuscript.
- Keep exact task ranges, factorial details, and retention-ratio sensitivity in
  the appendix.
- Keep full cell tables, seed-level curves, hashes, run identifiers, and recipe
  compatibility history in repository evidence only.
- Do not remove the existing threshold-grid-edge limitation.
- Replace, rather than append to, the existing discussion and future-work
  paragraphs so the paper does not accumulate repeated caveats.

## Blocked claims

The current evidence does **not** support any of the following:

- an optimal or selected training-noise strength;
- a post-hoc robustness band;
- superior checkpoint selection or improved planning from the Boolean screen;
- superiority over all training metadata;
- a homogeneous 17-level sweep;
- causal, universal, or certificate-level robustness claims.

## Score calibration

If integrated subtractively and without the blocked claims, this extension
genuinely strengthens the SR evidence and should make a score-6 diagnostic
paper more defensible, with a plausible 6--6.5 reading. It is not sufficient by
itself for a stable 7: it adds diagnostic activity and descriptive behavioral
association, not a prospective selection or planning intervention.
