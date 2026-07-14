# Paper1 Submission Remediation Handoff — 2026-07-13

This file is the durable resume point for the current Paper1 submission pass.
It records decisions, completed work, active commands, and the exact remaining
workflow so a new session does not repeat the audit or rerun completed jobs.

**Scientific-remediation continuation:** the corrected post-submission plan is
recorded in PAPER1_ACPC_SCIENTIFIC_REMEDIATION_PLAN_20260713.md. In
particular, P1 shows a large ACPC-H8 advantage over H1 and
structure-destroyed controls; it must not be summarized as a simple baseline
catching up. Only strong planner-linked theory, strong evidence, and
claim-bearing figures/tables are eligible for restoration.

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
  blind PDF, all unrelated Paper2/environment/worldmodels files, and the
  superseded operational decision-stability dev branch. Four post-freeze
  source/test files no longer match its immutable protocol and
  must be revived through a new addendum, never by mutating frozen hashes.

## Publication record

- Main submission commit: `162e4a7d29ca4033980bff608460197404f6d478`.
- Both `origin/ag/dev` and `holo/ag/dev` accepted the fast-forward from
  `e8566ef` to `162e4a7`; independent `ls-remote` queries returned the same
  full SHA.
- The configured HTTPS proxy repeatedly returned 503. Publication succeeded
  through per-command `NO_PROXY=github.com`; no persistent Git or network
  configuration was changed.

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
- [x] Commit with a concise Paper1 submission-remediation message.
- [x] Push the current branch to both existing remotes and verify full SHAs.
- [x] Record remaining non-writing scientific blockers/opportunities above.

## Expected final scientific boundary

The paper is a frozen-checkpoint diagnostic study, not a new robust-training
method. It supports: (i) a target-free samplewise bound and a matched
future-drift increment in the logged fragile regime; (ii) family-local
calibration across held-out training seeds; and (iii) a fixed-strength paired
ordering result across blur and resize. It does not support universal raw
thresholds, unseen-task generalization, adaptive-CEM guarantees, a
single-frame safety certificate, or absolute cross-stressor robustness.

## Scientific-remediation execution checkpoint (2026-07-13)

This is the resume point for the strengthened ACPC mainline described in
`PAPER1_ACPC_SCIENTIFIC_REMEDIATION_PLAN_20260713.md`.

- New fixed-pool runner:
  `tools/paper1_acpc_planner_stability_audit.py`. It records same-pool
  candidate-conditioned H1/H5 ACPC, the sharp squared-distance cost bound,
  top-1/elite certificates, and observed fixed-pool stability.
- New adaptive runner:
  `tools/paper1_acpc_adaptive_cem_audit.py`. It uses a common zero initial
  proposal and common random numbers, records the valid aligned-pool induction,
  final first-action RMS, and clean-history decision regret.
- Real-checkpoint TwoRoom smoke passed for both runners: fixed 4/4 rows
  complete with zero identity violations; adaptive 4/4 rows complete with
  identity first-action RMS 0 and identical updates at every CEM step.
- Frozen planner protocol:
  `paper1/config/acpc_planner_stability_protocol_v1.json` plus
  `acpc_planner_stability_execution_v1.json`. It binds eight seed3074
  base/endpoint checkpoints and 24 shards: eight K64 fixed-pool, eight K64 x
  8-step adaptive, and eight K300 x 30-step adaptive transfer shards.
- Frozen prospective-training protocol:
  `paper1/config/p1_prospective_seed3075_protocol_v1.json`. All four seed3075
  output directories were absent at freeze. The protocol trains four
  noise-free LeWM bases with seed3075 and evaluates the unchanged 16-block,
  four-severity, two-draw P1 design. Online loggers are disabled but the model,
  data, optimizer, epochs, and loss remain the seed3074 baseline contract.
- Provenance is explicit: seed3075 is fully prospective; seed3074 is a
  protocol-frozen replication; seed3073 has development-era provenance;
  seed3072 remains a retrospective completeness check.
- Validation at this checkpoint: 60/60 ACPC protocol, runner, summary, and
  target-aligned P1 tests passed (one third-party Gym warning only).

The next executable steps are: commit and push this frozen pre-result state to
both remotes; run the 24 authorized planner shards and four authorized seed3075
training jobs; summarize every result without changing thresholds; then rewrite
theory, figures, tables, main text, and appendix only from claim-eligible
evidence. Failed repair/PLDM/JVP branches stay excluded, while the qualitative
t-SNE remains in the appendix with an explicitly non-quantitative caption.

### Live execution and numerical-correction checkpoint (2026-07-13 17:40 UTC)

- Pre-result commit `a933c3bdbbdc11fbb78870f0a79783db62740c5f` is on both
  `origin/ag/dev` and `holo/ag/dev`.
- Four fully prospective seed3075 baseline trainings are active under the
  frozen commands: TwoRoom/GPU4, PushT/GPU5, Reacher/GPU6, and Cube/GPU7.
  All four passed data/model initialization and entered optimization; TwoRoom
  had already completed two checkpoint callbacks at the latest poll.
- The entire planner v1 panel executed. All 16 adaptive shards completed:
  eight K64 x 8-step shards have 400/400 rows and eight K300 x 30-step shards
  have 32/32 rows. All eight fixed-pool shards retained their 100 identity rows
  but rejected each of the three nonzero severities with the same
  `signed perturbed-gap identity mismatch`, producing 100/400 rows.
- Root cause is numerical rather than outcome-dependent: the exact identity
  `(c'_j-c'_w)=(c_j-c_w)+(delta_j-delta_w)` was evaluated through separately
  rounded float32 differences. A deterministic 512 x 64 regression tensor
  produces a `0.0078125` v1 residual despite the expressions being identical.
- Never overwrite or relabel v1. Its 24 JSON artifacts are bound by path and
  SHA-256 into `acpc_planner_stability_protocol_v2.json` as the superseded
  attempt. The only v2 change is to evaluate the signed-gap algebra and derived
  differences in float64 after the original float32 candidate costs are
  computed; pools, checkpoints, severities, seeds, estimands, thresholds, and
  claim gates are unchanged.
- v2 is frozen before its result directory exists:
  `paper1/config/acpc_planner_stability_protocol_v2.json` and
  `paper1/config/acpc_planner_stability_execution_v2.json`. It authorizes all
  24 shards again so one manifest and one untouched summary path cover the
  complete panel. Fixed shards use
  `tools/paper1_acpc_planner_stability_audit_v2.py`; adaptive shards retain the
  original runner.
- The v2 cancellation regression and protocol/source-hash tests pass (7/7 in
  the combined v1/v2 freeze check). The next safe action is to commit and push
  this correction freeze before launching any v2 shard.

### Submission-strengthening execution checkpoint (2026-07-13)

This section supersedes the previous live-status paragraph while preserving it
as execution provenance.

- Planner-v2 freeze commit `99d2a0c` is on both remotes. All 24 v2 shards
  completed and validate, with 3,200 exactly joined reduced-budget rows.
  Squared-cost-bound violations, false top-1 certificates, and false elite
  certificates are all zero; identity H5 ACPC and first-action RMS are zero,
  and all identity adaptive updates remain aligned.
- The predeclared leave-one-task-out H5 increment passes for fixed-pool maximum
  cost drift (9.4965% equal-task MAE reduction; 3/4 tasks) and adaptive
  positive clean-history regret (12.9230%; 4/4 tasks). First-action RMS is
  retained but does not clear the 5% effect gate (0.8136%; 4/4 tasks).
- At severity 0.08, endpoint/base equal-task positive regret is 2.85/208.86 at
  reduced budget and 1.01/218.69 at the deployed K=300, 30-step budget.
  Endpoint top-1 certificate coverage spans 19--70% across tasks with no false
  passes; coverage is zero for the fragile bases at that severity.
- The paper now has the sharp squared-goal-cost theorem, top-1/elite
  certificates, conditional adaptive-CEM induction, sharpness examples, a
  vector method diagram, a four-panel planner figure, a compact full-sweep
  table, and a per-task planner absolute table. The complete sweep stays in the
  main paper; the t-SNE stays qualitative in the appendix. Failed repair,
  PLDM, JVP/local-sensitivity, and other weak branches remain excluded.
- The current normal build is 14 pages. Appendix ordering was changed so the
  fixed-pool table fills the former page-13 blank region and the enlarged t-SNE
  occupies page 14. The method, planner, full-sweep, and t-SNE figures have
  received local rendered visual inspection.
- Prospective seed3075 training was interrupted only by the frozen four-hour
  infrastructure timeout. Exact Lightning resume is explicitly allowed by the
  frozen protocol and logs confirm `Restored all states`. Checkpoint state at
  this handoff: TwoRoom is running its final epoch in PTY session `23328`;
  PushT, Reacher, and Cube retain complete epoch-2 checkpoints. Their earlier
  short resume attempts were externally SIGTERM-terminated before a new epoch
  boundary and did not replace the saved checkpoints.
- Continue training one task at a time in a PTY with the exact protocol command,
  `STABLEWM_HOME` bound to the task root, its frozen GPU, two native threads,
  and the existing 14,400-second timeout. Do not change workers, optimizer,
  seed, data, epoch count, or model parameters. After all epoch-10 object
  checkpoints exist, run each frozen evaluation command from
  `p1_prospective_seed3075_protocol_v1.json` serially, then run its seed3075
  and combined summary commands unchanged.
- The P1 table renderer is already provenance-aware: seed3075 is prospective,
  seed3074 is the frozen replication, seed3073 is development-era, and
  seed3072 remains separate/retrospective. Once results exist, update the
  abstract, setup, P1 result, discussion, appendix control paragraph,
  three-pillar bundle, and manifest from generated artifacts rather than
  hand-entering values.
- Final remaining gates: targeted and full consistency tests, normal/blind
  14-page clean builds, warning/citation checks, all-page visual preflight,
  explicit Paper1-only staging, one final commit, and verified pushes to both
  remotes.

### Prospective-resume checkpoint (2026-07-13 17:02 UTC)

- TwoRoom exact-resume completed normally at `max_epochs=10`. The frozen
  epoch-10 object checkpoint is present at the protocol path (72,361,012
  bytes), alongside the full optimizer/scheduler resume checkpoint.
- The frozen execution contract explicitly authorizes four parallel jobs with
  one process per GPU and two native threads per process. The earlier resume
  instability was specific to non-PTY launches, not parallel execution.
  PushT, Reacher, and Cube are therefore active in PTY sessions `35415`,
  `80272`, and `54571` on GPUs 5/6/7, respectively; all three report
  `Restored all states` and resume from epoch 2. Keep the same 14,400-second
  hard timeout and exact-resume again at the latest completed epoch if needed.
- The resolved configs for seeds 3073/3074/3075 all contain the intended
  `cfg.seed`; in `train.py` it directly seeds the deterministic train/validation
  split generator. Stable-pretraining separately logs that its own Manager
  seed is unset after model construction. This is inherited from the frozen
  historical training pipeline, so it must not be patched mid-protocol. Treat
  the runs as separately trained checkpoints indexed by `cfg.seed`, and list
  fully deterministic initialization as a later engineering/reproducibility
  improvement rather than changing the present evidence after freeze.
- Submission code now calls the squared-goal-cost result a **sharp** bound,
  not an exact bound: the proof gives a worst-case equality construction while
  avoiding the misleading suggestion that the upper bound equals every
  observed cost drift. The new manifest builder binds the prospective P1
  protocol/results, planner-v2 protocol/summary, and submission-facing
  figures/tables once all prospective artifacts exist.

### Theory/visual continuation checkpoint (2026-07-13 21:51 UTC)

- The theory chain now also proves the directly planner-facing fixed-pool
  clean-history regret bound
  `0 <= C_{tilde w} - C_w <= b_{tilde w} + b_w`, where `w` and `tilde w` are
  the nominal and perturbed winners of one shared pool. This is a corollary of
  the same sharp candidate-wise squared-goal-cost bounds and does not modify a
  frozen runner or introduce a fitted constant. A new numerical regression
  test verifies the implication against the existing cost-bound implementation.
- The Introduction and experiment roadmap now name four distinct questions:
  future-drift mechanism, planner relevance, family-local calibration, and
  stressor scope. This removes the stale pre-planner three-question framing.
  Failed repair, generic Lipschitz/JVP/local-sensitivity, PLDM, and weak
  candidate-query branches remain excluded.
- The submission-facing method schematic was removed after final risk/benefit
  review; the equation and adjacent theorem statements now carry the method
  definition directly. The complete four-task full-sweep and planner figures
  were rebuilt on taller native canvases after rendered-page inspection showed
  excessive float-page whitespace. Curves, ranges, task markers, and labels are
  unchanged; only layout/plotting area changed. The
  compact nine-level sweep table and absolute planner table remain in the
  appendix, and the t-SNE remains explicitly qualitative/non-metric.
- The current normal PDF still has exactly 14 letter-size pages. Its latest
  LaTeX pass has no undefined citation/reference, overfull/underfull box,
  fatal, or undefined-control-sequence diagnostics. Method, theory, full-sweep,
  and planner pages were visually inspected at rendered submission size.
- The focused theory/asset shard passes 24/24 tests. The frozen scientific-plan
  SHA-256 remains
  `e3f7d4d715c9786489235b46106abe79e4facc9f9a423fc3ab8ac9ae320fa485`;
  do not edit that source-hash-bound plan.
- TwoRoom seed3075 training and frozen P1 evaluation are complete; the result
  artifact passes all recorded invariants. At this checkpoint PushT is in
  epoch 3, while Reacher and Cube are near the end of epoch 2, in PTY sessions
  `35415`, `80272`, and `54571`. Continue exact resume if the 14,400-second
  protection timeout fires. Do not summarize or hand-edit P1 claim numbers
  until all four frozen evaluations and both protocol summary commands finish.

### Claim/protocol audit checkpoint (2026-07-13 22:35 UTC)

- A 56-test non-GPU shard covering frozen ACPC protocols, planner-v2,
  adaptive-CEM, theory regret, P1 MVE/summarization, three-pillar reporting,
  and submission assets passes in full (one unrelated Gymnasium cast warning).
- The repository-wide consistency checker exposed byte-level drift in the two
  paired-multiseverity shell wrappers. The exact protocol-bound Git blobs were
  recovered and compared: each committed wrapper differed only by one removed
  EOF blank line, with no command, parameter, or execution-semantic change.
  Restoring that blank line gives the frozen SHA-256 values
  `0f9fab1257394ac358963da3f5c0be224fd1346d8f450ddc343c0d109faad48e`
  (behavior) and
  `38986f63cfce326a5987d676e9d4de81011c77b3396b6f86a08883aa535ec7ba`
  (ATR); the paired-multiseverity protocol check now passes. The only current
  consistency failure is the expected stale diagnostic-manifest binding, which
  must be rebuilt after final P1 tables/results exist.
- The method text now explicitly separates raw ACPC from checkpoint-level ATR:
  the raw numerator, future-drift theorem, and planner quantities require no
  realized future; normalized ATR reuses each fixed logged clean anchor's
  transition scale for cross-task comparability, so it is an offline logged-data
  checkpoint audit rather than an online single-history alarm.
- Earlier weak candidate-H5 failure details were removed from the submission.
  The paper retains only the necessary estimand boundary between logged-future
  prediction and the separately frozen same-pool planner panel. The planner-v2
  first-action-RMS result remains reported because it was predeclared; suppressing
  that outcome would be selective reporting.
- Prospective training remains healthy in PTY sessions `35415`, `80272`, and
  `54571`. Persisted object checkpoints now include PushT epochs 1--4 and
  Reacher/Cube epochs 1--3. Keep the exact frozen commands and resume only at
  the latest completed checkpoint if a hard timeout fires.

### Submission-scope checkpoint (2026-07-13 23:17 UTC)

- The blind source bundler no longer copies `tables/*.tex`. It now collects only
  the six table inputs and four figures actually referenced by `main.tex`, so
  unused JVP, PLDM, failed-repair, and legacy-baseline tables cannot enter the
  anonymous source tarball. The collector has a dedicated omission test (4/4
  tests pass), and the exact isolated blind bundle compiles successfully at 14
  pages with no identity or layout diagnostics.
- P1 wording no longer calls the new seed3075 checkpoint behaviorally fragile:
  the seed3075 protocol adds no closed-loop evaluation. The main claim is now
  precisely the logged future-drift increment on no-noise bases under the
  frozen visual-probe grid; the pre-existing seeds3072--3074 full sweep supplies
  the separate behavioral fragility/recovery context.
- A short README in `target_aligned_acpc_prospective_v1` binds protocol SHA-256
  `9976fe09ef6f90f3d7cac898a6452b55339d5107fc2f54b90ee0f518c201102b`,
  explains the inherited raw-runner `DEV` purpose string, forbids editing raw
  provenance, and records that all four task outcomes must be retained. The
  manifest builder hashes this note.
- Current persisted training state is epoch5 for PushT, Reacher, and Cube; all
  object checkpoint sizes are normal. PushT's prior PTY exited with code 1 only
  after its epoch5 object checkpoint was complete; Reacher/Cube then reached
  their watchdog boundary with complete epoch5 checkpoints. Exact frozen-command
  resumes have all reported `Restored all states` without traceback and now run
  in PTYs `72918`, `37401`, and `53095` on GPUs 5/6/7. Read-only monitor session
  `59288` is waiting for all three epoch6 checkpoints. The final generation
  order is frozen as P1 summaries, three-pillar tables, prose/tests, submission
  assets, then the hash manifest last.

### Resume checkpoint (2026-07-14 01:14 UTC)

- The prior PushT resume in PTY `72918` exited during epoch 6 after a single
  `DataLoader worker` segmentation fault. The last complete epoch-5 object
  checkpoint remains intact; no model, data, seed, or protocol parameter was
  changed. Reacher and Cube continue normally in PTYs `37401` and `53095`.
- PushT was exact-resumed once more with the protocol command on GPU 5 in PTY
  `35727`. Lightning reports `Restored all states` from the frozen checkpoint,
  training has re-entered epoch 6, and no traceback was present at startup.
  Continue to treat any further infrastructure exit as an exact-resume event,
  never as authorization to change the frozen training configuration.
- The CairnLab-derived writing/review/figure rules were re-audited during the
  GPU wait. Finalization must include a reverse-outline and claim--evidence
  pass, de-AI wording scan, final-size visual inspection, vector/font checks,
  self-contained captions, blind-source compilation, and explicit omission of
  unused legacy tables/figures. The t-SNE remains qualitative and the complete
  four-task sweep remains in scope.

### Three-seed planner completion checkpoint (2026-07-14 06:18 UTC)

- The planner mechanism panel now treats training seeds 3072/3073/3074
  symmetrically. Seed3074 contributes the 24 validated v2 reference shards;
  48 matching shards for seeds3072/3073 were executed under the frozen v4
  extension, giving 72 validated shards and 9,600 joined reduced-budget
  history records. All 48 new processes exited successfully.
- The unexecuted v3 freeze was superseded before any v3 result existed because
  its source manifest omitted the transitive single-seed summarizer. The v4
  correction changes no checkpoint, seed, candidate budget, response, feature,
  split, or gate; it adds the missing source binding and records v3 as
  superseded. Do not edit the v4-bound runner, summarizers, freeze scripts, or
  tests after this point.
- Fixed-pool maximum-cost-drift MAE reductions are 6.6%, 7.6%, and 9.5%
  (7.9 +/- 1.4% across seeds): all three seed means are positive, two of three
  seed gates pass, and 8/12 task--seed cells improve. This is reported as a
  directionally consistent, partially replicated increment, not a universal
  task-level result.
- Adaptive positive decision-regret reductions are 15.7%, 16.9%, and 12.9%
  (15.2 +/- 2.0%): all three seed gates and all 12 task--seed cells pass.
  First-action-RMS remains the predeclared negative result at 1.1 +/- 0.5%,
  with zero of three seed gates passing.
- The squared-cost bound, top-1 and elite certificates have zero violations or
  false passes. Identity probes have zero five-step ACPC and zero first-action
  RMS, and every active identity adaptive update remains aligned. Re-running
  the v4 summarizer from all 72 raw/reference shards produced byte-identical
  JSON and CSV summaries.
- The paper, Figure 4, both planner tables, submission-asset builder, script
  README, and final scientific remediation plan now use the three-seed
  aggregation. The active targeted regression shard passes 13/13 tests. The
  historical v2 source-hash assertion remains an archived pre-existing failure
  because its frozen manifest names an earlier summarizer hash; active v4
  explicitly binds the current transitive source and passes. Do not rewrite a
  historical frozen manifest to conceal that provenance transition.
- The rebuilt normal PDF is 19 letter-size pages, matching the immediately
  preceding arXiv/full-report page count. Figure 2 was reduced to 95% width to
  avoid a one-page float cascade; the scientific content is unchanged. Final
  visual inspection found the three-seed planner panel and appendix table
  readable, and the LaTeX log contains no overfull/underfull, undefined
  citation/reference, or fatal diagnostics.
- The only paper-local human blocker remains replacing the arXiv author
  placeholder. Separately, the previously exposed GitHub PAT must be revoked
  or rotated on GitHub even though the local remote URL has been sanitized.
