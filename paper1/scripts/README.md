# Paper1 Diagnostic Remediation Scripts

Submission-facing scripts rebuild diagnostics and displays from the three
independent training runs (seeds 3072/3073/3074). They do not train a new
checkpoint. Separately named paired_multiseverity runners reuse fixed
checkpoints, rerun bounded closed-loop evaluation, and never train.

## Current submission-facing ACPC bundle

The submission mainline is rebuilt from the future-drift adjudications, the
complete Gaussian sweep, the planner summary, and the 24-pair stressor file:

```bash
python -m paper1.scripts.build_future_drift_reader_display
python -m paper1.scripts.cross_task_selective_rule
python -m paper1.scripts.build_cross_stressor_selective_transfer
python paper1/scripts/build_acpc_submission_assets.py
bash paper1/build.sh
```

The first three commands rebuild the symmetric three-seed future-drift
display, all 14 cross-task threshold partitions, and the final-score-only
blur/resize transfer analysis. The fourth writes the vector method and
planner-evidence figures plus compact planner and full-sweep tables. These
steps perform no model evaluation or training. The planner inputs are the 24
validated shards under
`paper1/results/acpc_planner_stability_v2/`; the numerical v2 wrapper changes
only signed cost-gap algebra to float64 after the unchanged float32 model-cost
path.

To inspect or reproduce one frozen planner task queue:

```bash
python paper1/scripts/run_acpc_planner_stability_shards.py plan \
  --task TwoRoom \
  --protocol paper1/config/acpc_planner_stability_protocol_v2.json \
  --device 0
```

The legacy three-pillar evidence generator is archived and is not part of the
current paper dependency graph. The retained theory chain gives the sharp
candidate-cost bound, a shared-pool clean-regret bound, top-1/elite
certificates, and conditional adaptive-CEM alignment. Its empirical support is
the three-seed future-drift increment, planner panel, exhaustive cross-task
calibration, complete Gaussian sweep, and blur/resize selective-score transfer.

Run the CPU-only manifest/checker path from repository root:

```bash
bash paper1/scripts/run_all_paper1_diagnostics.sh
```

Rebuild checkpoint-level public-v1 audits only when the checkpoints and datasets are available:

```bash
PAPER1_DIAGNOSTIC_GPU=0 PAPER1_DIAGNOSTIC_THREADS=2 \
RUN_REMEDIATION_AUDITS=1 bash paper1/scripts/run_all_paper1_diagnostics.sh
```

This path is deliberately serial: one task/seed shard runs at a time on one GPU, every shard has a timeout, complete shards are validated and skipped, and native math libraries default to two threads. `RUN_CHECKPOINT_AUDITS=1` remains a compatibility alias for the same bounded path; it no longer launches the retired monolithic jobs.

External E3/E4 checkpoint recomputation is separately opt-in:

```bash
PAPER1_DIAGNOSTIC_GPU=0 PAPER1_DIAGNOSTIC_THREADS=2 \
RUN_EXTERNAL_AUDITS=1 bash paper1/scripts/run_all_paper1_diagnostics.sh
```

Rebuild the E3 aggregate, paired-change uncertainty, exact/deletion/selection
robustness audit, generated tables, and scatter from completed
diagnostic/evaluation artifacts (no training or evaluation):

```bash
python -m paper1.scripts.build_cross_stressor_external_validation \
  --baseline-diagnostics paper1/results/diagnostic_baselines/diagnostic_baseline_all_v1.json \
  --force
```

Archived summary/plot regeneration can overwrite legacy figures and is therefore also explicit: `REBUILD_LEGACY_AGGREGATES=1`. No flag reruns closed-loop evaluation or training.

Archived public-v1 checkpoint steps retained for provenance:

```bash
bash paper1/scripts/run_jvp_hutchinson_shards.sh
bash paper1/scripts/run_diagnostic_baseline_shards.sh
bash paper1/scripts/run_fixed_pool_certificate_shards.sh
bash paper1/scripts/run_smpr_controls_mve.sh
bash paper1/scripts/run_linearization_horizon_shards.sh
```

Legacy summary-level steps retained for provenance:

```bash
python -m paper1.scripts.build_diagnostic_manifest
python -m paper1.scripts.build_full_sweep_diagnostics
python -m paper1.scripts.plot_full_sweep_diagnostics
python -m paper1.scripts.plot_endpoint_atr_smpr
python -m paper1.scripts.fixed_pool_tail_audit
python -m paper1.scripts.heldout_diagnostic_validation
python -m paper1.scripts.threshold_quantile_sensitivity
python -m tools.paper1_sample_level_certificate --out-json paper1/results/sample_level_certificate_full_sweep_audit.json --out-csv paper1/results/sample_level_certificate_full_sweep_audit.csv --sample-csv paper1/results/sample_level_certificate_full_sweep_samples.csv
python -m paper1.scripts.full_sweep_sample_level_certificate_summary
python -m paper1.scripts.sample_level_event_rate_ci
python -m paper1.scripts.plot_fixed_pool_event_rates
python -m tools.paper1_gaussian_sensitivity_audit --num-noise-draws 5
python -m tools.paper1_jvp_hutchinson_sensitivity_audit --n-sequences 100 --hutchinson-probes 8
python -m paper1.scripts.joint_guard_side_validation
python -m paper1.scripts.plot_gaussian_sensitivity_mechanism
```

Frozen prospective multi-severity extension (all commands are serial,
resumable, hash-gated, and watchdog-bounded):

~~~bash
# No eval: inspect checkpoint binding and pending behavior artifacts.
bash paper1/scripts/run_paired_multiseverity_behavior.sh plan

# One frozen seed/task/stressor/severity smoke.
bash paper1/scripts/run_paired_multiseverity_atr.sh smoke
bash paper1/scripts/run_paired_multiseverity_behavior.sh smoke
bash paper1/scripts/run_paired_multiseverity_smpr_v2.sh smoke

# Complete LeWM diagnostics first, then closed-loop behavior.
bash paper1/scripts/run_paired_multiseverity_atr.sh full
bash paper1/scripts/run_paired_multiseverity_smpr_v2.sh full
bash paper1/scripts/run_paired_multiseverity_behavior.sh full

# This refuses partial coverage; success requires all 72 paired rows.
python -m paper1.scripts.build_paired_multiseverity_summary
~~~

The parent protocol is paper1/config/paired_multiseverity_protocol_v1.json
(SHA-256 6712b4f595444d751d9c327262c288e37dbd80be7ddde9bb4fd336ed41119622).
The SMPR execution addendum transparently records that its wrapper/reference
adapter was connected after the behavior/ATR smoke had been inspected; it does
not alter the zero threshold, severity grid, sampling, or analysis. A smoke is
never primary-claim eligible, and PLDM must not start before the complete LeWM
72-row aggregate is locked.

The original `run_paired_multiseverity_smpr.sh` is retained as v1 provenance.
Its reference key omitted task; the v2 addendum records the stopped run and the
v2 runner binds every reference by seed, task, stressor, and severity.

Plot output notes:

- `plot_full_sweep_diagnostics` writes vector PDF figures by default: a main figure with separate behavior and ATR/SMPR axes per task, the diagnostic-region scatter, and a compact four-across appendix planner-guard figure; recovery shading is rendered as continuous majority-recovered ranges. The main sweep display divides ATR by each task$\times$seed no-noise value (base 1) while leaving SMPR on its original rate scale; frozen calibration uses the unrescaled ATR statistic.
- `plot_cross_stressor_submission` reads the locked all-pairs CSV and writes the 24-pair LeWM submission scatter as a vector PDF; it does not rerun diagnostics or evaluation.
- `plot_endpoint_atr_smpr` writes the two-panel endpoint dumbbell figure with base-to-noise-trained movement arrows.
- `plot_gaussian_sensitivity_mechanism` writes a two-panel endpoint/base lollipop figure for the main text and the trace-decomposition heatmap plus separate alignment panel for the appendix.
- `plot_fixed_pool_event_rates` writes the two-panel paired event-rate figure; conditional flip-given-cert-pass rates remain in the appendix table.

Important scope constraints:

- The immutable public-v1 protocol SHA-256 is `edcb801c3da388e673c9b55d706a558aa01da7a281fc151e52e1cda566045a21`; checkpoint builders must reproduce this value in external artifacts.
- Matched component/horizon baselines do not establish empirical necessity for H=8 or correct-action conditioning.
- E3 distinguishes model-family-calibrated absolute screening from a reference-based paired comparison; one zero threshold is shared across fixed LeWM blur/resize stressors, not across absolute model-family scales.
- The sharp certificate applies only to the sampled ordered candidate pool; zero flips on cert-pass are a deterministic invariant check.
- SMPR v2 rejects constant collapse but does not establish incremental action, label, progressive-collapse, or four-task oracle relevance.
- Full-sweep diagnostics join existing Gaussian evaluation, ATR, SMPR, and retained fixed-pool summaries.
- Full-sweep sample-level fixed-pool event rates are recomputed from checkpoints; strict q10/q95 gaps remain negative and are not treated as calibrated probability bounds.
- Wilson intervals quantify sample event-rate estimation uncertainty; they are not calibrated theorem probability bounds. The event-rate figure is regenerated from `paper1/results/sample_level_event_rate_wilson_ci.csv`.
- Held-out validation freezes diagnostic gates on calibration rows before evaluating held-out rows.
- Gaussian sensitivity is audited with finite differences using 100 sampled sequences and 5 noise draws per small sigma, plus an exact-autograd JVP/Hutchinson trace decomposition using 100 sampled sequences and 8 Rademacher probes per checkpoint; both are local checkpoint audits, not closed-loop guarantees.
- SMPR and fixed-pool top-1 flip are guard-side checks interpreted only jointly with ATR, not standalone robustness metrics.
- ATR q80/q95 and positive-margin SMPR variants are not inferred from retained ATR/SMPR summaries.
