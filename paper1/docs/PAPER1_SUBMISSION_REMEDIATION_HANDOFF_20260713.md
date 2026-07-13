# Paper1 Submission Remediation Handoff — 2026-07-13

This file is the durable resume point for the current Paper1 submission pass.
It records decisions, completed work, active commands, and the exact remaining
workflow so a new session does not repeat the audit or rerun completed jobs.

## Objective and authorization

- Bring `paper1/main.tex` and its figures/tables to top-conference submission
  quality, including claim compression, main/appendix separation, visual
  polish, PDF inspection, and anonymity checks.
- Preserve valid work already present in the working tree; use a delta audit,
  not a rewrite from the committed baseline.
- After validation, make an explicit Paper1-only commit and push the current
  branch to both existing remotes. The user explicitly authorized both pushes.
- After publication, report non-writing scientific/evaluation gaps separately.

Baseline commit: `e8566ef63ab00cdf73d763f0d521669f57254eb4`

## User decisions that must be preserved

1. **P1 primary provenance remains unchanged.** The primary pooled result uses
   seeds 3073/3074. Seed3073 contains development provenance; seed3074 is the
   fully protocol-frozen four-task replication.
2. **Seed3072 is not a third confirmatory P1 replication.** Its new four-task
   run is a post-outcome retrospective completeness check. It may be reported
   separately in supplementary/repository material, but it must not change the
   P1 primary estimand or be pooled as three independent confirmatory seeds.
3. **P2 is the CAL/TEST split.** Seed3072 is CAL only; seeds3073/3074 are
   held-out TEST. Do not mix all three into an ordinary three-seed test mean.
4. **Keep the t-SNE visualization.** It is useful qualitative intuition. Keep
   it appendix-only (unless a later layout decision explicitly promotes a
   small inset), state that no quantitative claim is computed in t-SNE space,
   and improve its panel hierarchy, legend, fonts, and caption.
5. The remediation must cover figures and tables, not only prose.
6. Existing successful work should be accepted quickly after verification;
   only high-impact remaining issues should be reconsidered deeply.

## External writing/review requirements read for this pass

The latest CairnLab sources were read from commit `3eac0b0` because the current
`../CairnLab` checkout does not expand the source files:

- `skills/paper-writing-quality/SKILL.md`
- `skills/paper-writing-quality/references/writing-quality-checklist.md`
- `skills/autoresearch-landscape-survey/SKILL.md`
- `skills/autoresearch-landscape-survey/references/paper-writing-quality-module.md`
- `skills/autoresearch-landscape-survey/references/paper-review-remediation-protocol.md`

The binding implications for this pass are:

- structure and claim compression before display expansion;
- subtractive remediation before adding caveats or tables;
- one reader-facing job per section;
- negative results remain only when they rule out a key alternative reading;
- appendix extends evidence rather than storing audit history;
- figures show trends/regions/uncertainty/mechanisms; tables preserve compact
  exact values;
- captions identify scope, aggregation, sample/seed unit, supported reading,
  and the material non-claim boundary;
- remove internal review/provenance/manifest wording from paper-facing prose;
- inspect the rendered PDF, not only LaTeX source.

The local `github:yeet` publication instructions were also read. The user wants
direct pushes to both existing remotes and did not request a PR. Stage only the
explicit Paper1 scope; the worktree contains unrelated untracked files.

## Recovered starting state

- Current PDF before this final pass: `paper1/main.pdf`, 19 pages, built
  2026-07-13 around 02:50 local PDF metadata time.
- Main narrative is already reorganized around three claims:
  target-aligned future-drift mechanism (P1), held-out training-seed
  calibration (P2), and Gaussian-to-blur/resize transfer (P3).
- Existing primary P1 meta artifact remains
  `paper1/results/target_aligned_acpc_dev/meta_four_task_seeds3073_3074_goal25_base_endpoint_v1.json`.
- Prior targeted validation reported 25 tests passed (one warning) for the P1
  target-aligned scripts/tests.
- All eight seed3072 raw MVE files now exist and reported `status=PASS`:
  TwoRoom, PushT, Reacher, and Cube, each for base and endpoint.
- No active experiment process was found. An older Codex process remains
  stopped around an approval/read step; do not kill or rely on it.
- The normal filesystem sandbox helper currently exits with status 182 even
  for read-only commands. Read/validation commands therefore required approved
  `require_escalated` execution. This is an environment issue, not a repo test
  failure.

## Current active command / precise resume point

At the time this file was created, the following standalone seed3072
retrospective adjudication was launched under exec session `91214`:

```bash
PYTHONPATH=. python -m paper1.scripts.summarize_target_aligned_acpc_mve \
  paper1/results/target_aligned_acpc_dev/mve_tworoom_seed3072_base_goal25_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_tworoom_seed3072_endpoint_goal25_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_pusht_seed3072_base_goal25_prefix_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_pusht_seed3072_endpoint_goal25_prefix_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_reacher_seed3072_base_goal25_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_reacher_seed3072_endpoint_goal25_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_cube_seed3072_base_goal25_v3_16block.json \
  paper1/results/target_aligned_acpc_dev/mve_cube_seed3072_endpoint_goal25_v3_16block.json \
  --out paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3072_goal25_base_endpoint_v1.json
```

Do **not** resume the interrupted three-seed meta command. The standalone
adjudication is sufficient for the retrospective check.

**Update:** session `91214` was terminated by the environment with exit 137
before writing its output. The eight raw PASS artifacts remain intact. Do not
repeat the MVE runs. Retry the summary with a lower-peak-memory, per-task or
streaming path, and record seed3072 separately from the P1 primary result.

## Submission delta audit: accepted versus remaining work

### Accepted after quick verification

- The target-free reverse-triangle theorem and its action-matched target
  boundary.
- The separation of P1, P2, and P3 evidence units.
- Primary P1 numbers and the seeds3073/3074 conditional bootstrap wording.
- P2 seed3072 CAL to seeds3073/3074 TEST logic.
- P3 separation between endpoint-only scoring and paired reference-based
  change.
- Current main figures are scientifically interpretable and reproducibly
  generated; they need refinement, not replacement from scratch.
- The current t-SNE remains qualitative and appendix-only.

### High-impact remaining changes

1. Tighten the abstract and introduction. Reduce metric stacking, remove the
   endpoint false-pass detail from the abstract, keep one positive claim plus
   one boundary claim, and keep no more than three nonstandard abstract
   acronyms.
2. Remove manuscript-logistics prose and weak external-family obligations.
   PLDM's single-family slice does not meet the core three-pillar evidence
   standard and should move to repository provenance/future work.
3. Move the fixed-pool derivation out of the main method section. Consolidate
   it with its proof and empirical figure in one appendix section; retain it as
   a scoped operational interpretation, not a headline contribution.
4. Replace internal P1/P2/P3-style headings with reader-facing scientific
   headings where this improves the argument flow.
5. Remove/merge appendix material that behaves like an audit dump:

**Completed update (2026-07-13):** the low-memory per-task path completed for
all four tasks and was merged into
`paper1/results/target_aligned_acpc_dev/adjudication_four_task_seed3072_goal25_base_endpoint_retrospective_v1.json`.
The logged-$H=8$ absolute and adverse conditions pass on all four tasks for
seed 3072. The candidate-$H=5$ result remains task dependent: the absolute
condition passes TwoRoom/PushT, and the adverse condition passes only PushT.
The zero-violation implementation invariant holds for every base/endpoint row.
This result is now described in the appendix as a retrospective completeness
check and is explicitly not pooled with the seeds 3073/3074 primary estimate.

The submission-facing writing/display pass has also completed its main edits:

- abstract, introduction, results, discussion, and conclusion were compressed;
- the fixed-pool definitions/proofs were consolidated in the appendix;
- the 36-row Gaussian table, five duplicate diagnostic tables, one duplicate
  fixed-pool table, three local-sensitivity tables, the concurrent-work table,
  and the PLDM side branch were removed from the manuscript;
- the three core tables were regenerated with reader-facing captions/headers;
- the full-sweep figure now displays across-seed ranges, the cross-stressor
  figure displays the predeclared $\pm5$pp neutral band, and the retained t-SNE
  has concise titles and an explicit legend;
   - the full 36-row Gaussian numeric table (redundant with the main figure and
     source artifacts);
   - five legacy/diagnostic tables whose old metric families, saturated
     sensitivity results, or two-task MVE do not close the current claim;
   - the fixed-pool numeric table that duplicates its figure and prose;
   - three local/JVP sensitivity tables that duplicate the mechanism figure;
   - the concurrent-work comparison table already covered by Related Work;
   - weak PLDM rows and language.
6. Keep one compact LeWM cross-stressor component table because it rules out a
   key alternative reading: P3 association is not uniquely action-specific.
   Rewrite its labels/caption as reader-facing science.
7. Rewrite all surviving appendix headings/captions to scientific roles rather
   than audit/provenance/remediation language.

## Figure and table plan

### Main figures

- `fig_full_sweep_diagnostics.pdf`: keep the 2x2 task layout; add transparent
  across-training-seed variation without obscuring the mean; retain
  color+marker+linestyle redundancy; update caption with aggregation and
  variation semantics.
- `fig_cross_stressor_submission.pdf`: keep the compact scatter; make the
  zero diagnostic rule and five-point behavior region easier to read, without
  implying the displayed stressed-gain axis contains the separate clean-drop
  condition; keep colorblind-safe stressor encoding and task markers.

### Qualitative figure

- `fig_acpc_basin_tsne.png`: keep in appendix. Replace repeated long panel
  titles with concise checkpoint/feature hierarchy; add an explicit legend for
  background clean states, selected anchors, perturbed views, and 2-D
  covariance envelopes; preserve ATR/SMPR insets; state in the caption that
  distances/areas are not analyzed and diagnostics are computed in original
  feature space.
- Reuse `/tmp/paper1_selective_contraction_cache`; do not refresh feature
  extraction for style-only changes.

### Main tables

- P1: preserve per-task visibility and both comparators; improve reader-facing
  headers/caption and explain that positive values are MAE reductions.
- P2: replace “read-only application” wording with held-out application;
  expand metric semantics in the caption.
- P3: remove the interpretation-only `Boundary` column and move its meaning to
  prose/caption; use reader-facing rule names.

## Final validation snapshot before publication

- The normal and blind PDFs both build to 14 pages under the title
  *Target-Free Action-Conditioned Predictive Diagnostics for Visually Stressed
  World Models*. Their PDF `Author` metadata is empty.
- `paper1/main.log` and `paper1/main_blind.log` contain no overfull/underfull
  boxes, undefined references, LaTeX/package warnings, or fatal errors.
- `paper1/docs/check_blind_ready.sh` passed, including the isolated source
  bundle at `/tmp/paper1_blind_src.tar.gz`.
- The final page-size inspection covered all main/appendix displays. In
  particular, the retained t-SNE remains legible and explicitly qualitative,
  and the page-14 component table is readable after its font adjustment.
- The targeted suite passed 70 tests: three-pillar evidence (4),
  cross-stressor validation (15), target-manifest validation (8),
  target-aligned ACPC (16), target-aligned MVE (9), and external/candidatewise
  artifacts (18). The two emitted warnings are third-party pygame/gym warnings.
- `tools/check_paper1_consistency.py` passed every artifact, protocol, claim,
  canonical-JSON, heading, figure/table, and forbidden-text gate after the
  final manifest rebuild. `git diff --check` is also clean.
- The 2026-07-13 reference spot check re-opened the official arXiv records for
  the six recent action-consistency papers in Related Work; the current bounded
  wording remains supported.
- `gh` is not installed in this environment. Publication therefore uses the
  permitted direct-`git` fallback. Before staging, `HEAD`, `origin/ag/dev`, and
  `holo/ag/dev` were exactly aligned (`0/0` divergence for both remotes).
- The explicit commit scope includes reproducible submission-facing Paper1
  protocols, scripts, tests, generated tables/figures, and result artifacts.
  It excludes replay caches, files explicitly marked invalid, the duplicate
  blind PDF, and all
  unrelated Paper2/environment/worldmodels files.
  The superseded operational decision-stability dev branch is also excluded:
  four post-freeze source/test files no longer match its immutable protocol and
  must be revived through a new addendum, never by mutating frozen hashes.

## Remaining non-writing scientific priorities

1. Add prospectively frozen training seeds for the P1 primary estimand. The
   seed3072 retrospective check strengthens completeness but cannot replace
   independent confirmatory replication or population-level seed uncertainty.
2. Extend P3 beyond one fixed blur/resize severity and 24 LeWM pairs, ideally
   with absolute cross-stressor labels and an additional independently trained
   model family.
3. Test adaptive CEM/replanning and closed-loop outcomes directly; the current
   fixed-pool result is a post-evaluation certificate, not a planner guarantee.
4. Replace or supplement SMPR with semantic/simulator-grounded labels so that a
   stable-but-wrong latent prediction cannot appear reassuring.

## Remaining execution checklist

- [x] Recover worktree, current PDF, and prior experiment transcript.
- [x] Read CairnLab paper review/writing requirements and publication skill.
- [x] Confirm all eight seed3072 raw MVE files exist and passed.
- [x] Re-run seed3072 retrospective adjudication with a lower-peak-memory
  per-task/streaming path (the all-eight-files attempt exited 137).
- [x] Record its result without changing the P1 primary pooled numbers.
- [x] Apply main-text claim compression and fixed-pool demotion.
- [x] Apply appendix subtraction and heading/caption cleanup.
- [x] Patch reproducible plot/table generators.
- [x] Regenerate full-sweep, cross-stressor, and t-SNE figures.
- [x] Rebuild machine-readable summaries/manifest required by generators.
- [x] Run targeted P1/P2/P3 tests and `tools/check_paper1_consistency.py`.
- [x] Build normal and blind PDFs; inspect warnings, page count, anonymity, and
  every surviving figure/table at page size.
- [x] Run a final Paper1-only diff audit and writing-quality ledger.
- [x] Check `gh --version` and `gh auth status`; the CLI is absent, so use the
  direct-`git` fallback after confirming both remote branches are aligned.
- [x] Stage only intended Paper1/code/test/manifest files; exclude unrelated
  `paper2_data`, environment snapshots, `worldmodels/`, and other user files.
- [ ] Commit with a concise Paper1 submission-remediation message.
- [ ] Push the current branch to both existing remotes.
- [x] Record remaining non-writing scientific blockers/opportunities above.

## Expected final scientific boundary

The paper is a frozen-checkpoint diagnostic study, not a new robust-training
method. It supports: (i) a target-free samplewise bound and a matched
future-drift increment in the logged fragile regime; (ii) family-local
calibration across held-out training seeds; and (iii) a fixed-strength paired
ordering result across blur and resize. It does not support universal raw
thresholds, unseen-task generalization, adaptive-CEM guarantees, a
single-frame safety certificate, or absolute cross-stressor robustness.
