#!/usr/bin/env python3
"""Release consistency checks for Paper 1.

Usage:
    python -m tools.check_paper1_consistency
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RELEASE_FILES = [
    # PDF-facing text gate. Legacy diagnostics remain in repository artifacts,
    # but Paper1 must not re-import them into the main claim.
    ROOT / "paper1" / "main.tex",
]

REQUIRED_ARTIFACTS = [
    ROOT / "paper1" / "config" / "paired_multiseverity_protocol_v1.json",
    ROOT / "paper1" / "config" / "paired_multiseverity_protocol_v1.sha256",
    ROOT / "paper1" / "config" / "paired_multiseverity_execution_addendum_v1.json",
    ROOT / "paper1" / "config" / "paired_multiseverity_execution_addendum_v1.sha256",
    ROOT / "paper1" / "config" / "paired_multiseverity_execution_addendum_v2.json",
    ROOT / "paper1" / "config" / "paired_multiseverity_execution_addendum_v2.sha256",
    ROOT / "paper1" / "scripts" / "run_paired_multiseverity_smpr_v2.sh",
    ROOT / "paper1" / "scripts" / "run_paired_multiseverity_behavior.sh",
    ROOT / "paper1" / "scripts" / "run_paired_multiseverity_atr.sh",
    ROOT / "paper1" / "scripts" / "build_paired_multiseverity_atr_reference.py",
    ROOT / "paper1" / "scripts" / "run_paired_multiseverity_smpr.sh",
    ROOT / "paper1" / "results" / "multiseverity_v1" / "raw" / "lewm_seed3072" / "gaussian_blur_ks7" / "acpc_tworoom_v2.json",
    ROOT / "paper1" / "results" / "multiseverity_v1" / "raw" / "lewm_seed3072" / "gaussian_blur_ks7" / "smpr_tworoom_v2.json",
    ROOT / "paper1" / "results" / "multiseverity_v1" / "reference" / "lewm_seed3072" / "gaussian_blur_ks7" / "acpc_horizon_v2_checkpoint_bound.json",
    ROOT / "paper1" / "results" / "multiseverity_v1" / "reference" / "lewm_seed3072" / "gaussian_blur_ks7" / "acpc_tworoom_horizon_v2_checkpoint_bound.json",
    ROOT / "paper1" / "results" / "multiseverity_v1" / "manifests" / "behavior_s3072_tworoom_std0p0_gaussian_blur.json",
    ROOT / "paper1" / "results" / "multiseverity_v1" / "manifests" / "behavior_s3072_tworoom_std0p08_gaussian_blur.json",
    ROOT / "assets" / "paper1_data" / "canonical_evals_20260517.json",
    ROOT / "assets" / "paper1_data" / "canonical_evals_20260517.schema.json",
    ROOT / "assets" / "paper1_data" / "canonical_diagnostics_20260517.json",
    ROOT / "assets" / "paper1_data" / "canonical_diagnostics_20260517.schema.json",
    ROOT / "assets" / "paper1_data" / "canonical_external_baselines_20260520.json",
    ROOT / "assets" / "paper1_data" / "canonical_external_baselines_20260520.schema.json",
    # PLDM cross-method replication (added 2026-05-22)
    ROOT / "assets" / "paper1_data" / "canonical_evals_pldm_20260522.json",
    ROOT / "assets" / "paper1_data" / "canonical_diagnostics_pldm_20260522.json",
    ROOT / "assets" / "paper1_data" / "cross_method_corr_pldm_20260522.json",
    ROOT / "assets" / "paper1_data" / "canonical_full_diagnostics_pldm_20260523.json",
    ROOT / "assets" / "paper1_data" / "canonical_full_diagnostics_pldm_20260523.schema.json",
    ROOT / "assets" / "paper1_data" / "canonical_blur_baselines_20260523.json",
    ROOT / "assets" / "paper1_data" / "canonical_blur_baselines_20260523.schema.json",
    ROOT / "assets" / "paper1_data" / "acpc_basin_diagnostics.json",
    ROOT / "assets" / "paper1_data" / "acpc_basin_diagnostics_pldm.json",
    ROOT / "assets" / "paper1_data" / "partial_corr_bootstrap_20260523.json",
    ROOT / "assets" / "paper1_data" / "acpc_phase0_clean_goal_seed9101.json",
    ROOT / "assets" / "paper1_data" / "target_view_closed_loop_summary.json",
    ROOT / "assets" / "paper1_data" / "no_retrain_diagnostic_audit.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_tworoom.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_reacher.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_s3072.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_s3072.schema.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_s3072_manifest.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_s3073.json",
    ROOT / "assets" / "paper1_data" / "unseen_origin_vs_std008_strongest_s3074.json",
    ROOT / "assets" / "paper1_data" / "training_seed_gaussian_lockbox.json",
    ROOT / "assets" / "paper1_data" / "training_seed_gaussian_lockbox.md",
    ROOT / "assets" / "paper1_data" / "prospective_validation_summary.json",
    ROOT / "assets" / "paper1_data" / "prospective_validation_summary.md",
    ROOT / "assets" / "paper1_data" / "unseen_phase0_acpc_fullstress.json",
    ROOT / "assets" / "paper1_data" / "unseen_phase0_acpc_fullstress.schema.json",
    ROOT / "assets" / "paper1_data" / "training_seed_eval_manifests" / "lewm_seed3072_evals.json",
    ROOT / "assets" / "paper1_data" / "training_seed_eval_manifests" / "lewm_seed3073_evals.json",
    ROOT / "assets" / "paper1_data" / "training_seed_eval_manifests" / "lewm_seed3074_evals.json",
    ROOT / "assets" / "paper1_data" / "acpc_phase0_lewm_seed3072.json",
    ROOT / "assets" / "paper1_data" / "acpc_phase0_lewm_seed3073.json",
    ROOT / "assets" / "paper1_data" / "acpc_phase0_lewm_seed3074.json",
    ROOT / "assets" / "paper1_data" / "acpc_phase0_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "three_seed_diagnostic_validation.json",
    ROOT / "assets" / "paper1_data" / "three_seed_diagnostic_validation.md",
    ROOT / "assets" / "paper1_data" / "selector_baseline_audit_20260704.json",
    ROOT / "assets" / "paper1_data" / "selector_baseline_audit_20260704.md",
    ROOT / "assets" / "paper1_data" / "selector_plateau_audit_20260704.json",
    ROOT / "assets" / "paper1_data" / "selector_plateau_audit_20260704.md",
    ROOT / "assets" / "paper1_data" / "residual_diagnostic_audit_20260704.json",
    ROOT / "assets" / "paper1_data" / "residual_diagnostic_audit_20260704.md",
    ROOT / "assets" / "paper1_data" / "selector_incremental_audit_20260704.json",
    ROOT / "assets" / "paper1_data" / "selector_incremental_audit_20260704.md",
    ROOT / "assets" / "paper1_data" / "margin_flip_curve_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "semantic_margin_passrate_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "semantic_margin_passrate_lewm_three_seed.md",
    ROOT / "assets" / "paper1_data" / "semantic_local_margin_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_lewm_full_sweep_20260708.json",
    ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_lewm_three_seed.md",
    ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_unseen_blur_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_unseen_resize_lewm_three_seed.json",
    ROOT / "assets" / "paper1_data" / "unseen_atr_smpr_summary_20260707.json",
    ROOT / "assets" / "paper1_data" / "unseen_atr_smpr_summary_20260707.md",
    ROOT / "assets" / "paper1_data" / "cem_trace_audit_20260704.json",
    ROOT / "assets" / "paper1_data" / "cem_trace_audit_20260704.md",
    ROOT / "assets" / "paper1_data" / "compressed_metrics_summary_20260706.json",
    ROOT / "assets" / "paper1_data" / "compressed_metrics_summary_20260706.md",
    ROOT / "assets" / "paper1_data" / "base_noise_cliff_multistd_20260706.json",
    ROOT / "assets" / "paper1_data" / "base_noise_cliff_multistd_20260706.md",
    ROOT / "assets" / "paper1_data" / "three_seed_gaussian_sweep_summary_20260706.json",
    ROOT / "assets" / "paper1_data" / "three_seed_gaussian_sweep_summary_20260706.md",
    ROOT / "assets" / "paper1_figs" / "fig2_sweep.png",
    ROOT / "assets" / "paper1_figs" / "fig_cross_stressor_fixed_rho.png",
    ROOT / "assets" / "paper1_figs" / "fig_acpc_basin_tsne.png",
    ROOT / "assets" / "paper1_figs" / "fig_full_sweep_diagnostics.png",
    ROOT / "assets" / "paper1_figs" / "fig_full_sweep_diagnostic_region.png",
    ROOT / "assets" / "paper1_figs" / "fig_full_sweep_planner_guard.png",
    ROOT / "assets" / "paper1_figs" / "fig_endpoint_atr_smpr.png",
    ROOT / "assets" / "paper1_figs" / "fig_heldout_diagnostic_validation.png",
    ROOT / "assets" / "paper1_figs" / "fig_fixed_pool_tail_audit.png",
    ROOT / "assets" / "paper1_figs" / "fig_top1_agreement_full_sweep.png",
    ROOT / "assets" / "paper1_figs" / "fig_threshold_sensitivity.png",
    ROOT / "assets" / "paper1_figs" / "fig_radius_margin_interval_overlay.png",
    ROOT / "assets" / "paper1_figs" / "fig_radius_margin_overlap.png",
    ROOT / "assets" / "paper1_figs" / "fig_fixed_pool_event_rates.png",
    ROOT / "assets" / "paper1_figs" / "fig_gaussian_sensitivity_main.png",
    ROOT / "assets" / "paper1_figs" / "fig_jvp_trace_decomposition_heatmap.png",
    ROOT / "paper1" / "results" / "radius_margin_certificate_summary.csv",
    ROOT / "paper1" / "results" / "radius_margin_gate_ablation.csv",
    ROOT / "paper1" / "results" / "radius_margin_boundary_alignment.csv",
    ROOT / "paper1" / "results" / "fixed_pool_top1_agreement.csv",
    ROOT / "paper1" / "results" / "prospective_diagnostic" / "diagnostics_all_ckpts.csv",
    ROOT / "paper1" / "results" / "diagnostic_region" / "diagnostic_region_rows.csv",
    ROOT / "paper1" / "results" / "diagnostic_region" / "diagnostic_region_summary.csv",
    ROOT / "paper1" / "results" / "diagnostic_region" / "direction_consistency_by_block.csv",
    ROOT / "paper1" / "results" / "diagnostic_region" / "direction_consistency_summary.csv",
    ROOT / "paper1" / "results" / "diagnostic_region" / "robust_fragile_separation.csv",
    ROOT / "paper1" / "results" / "diagnostic_region" / "README.md",
    ROOT / "paper1" / "results" / "diagnostic_manifest.json",
    ROOT / "paper1" / "results" / "full_sweep_diagnostics.csv",
    ROOT / "paper1" / "results" / "full_sweep_diagnostics_summary.csv",
    ROOT / "paper1" / "results" / "heldout_diagnostic_validation.csv",
    ROOT / "paper1" / "results" / "heldout_gate_params.json",
    ROOT / "paper1" / "results" / "fixed_pool_tail_audit.csv",
    ROOT / "paper1" / "results" / "fixed_pool_tail_audit_summary.csv",
    ROOT / "paper1" / "results" / "threshold_quantile_sensitivity.csv",
    ROOT / "paper1" / "results" / "MISSING_DATA_fixed_pool_tail_audit.md",
    ROOT / "paper1" / "results" / "sample_level_certificate_endpoint_audit.json",
    ROOT / "paper1" / "results" / "sample_level_certificate_endpoint_audit.csv",
    ROOT / "paper1" / "results" / "sample_level_certificate_endpoint_samples.csv",
    ROOT / "paper1" / "results" / "sample_level_certificate_endpoint_summary.csv",
    ROOT / "paper1" / "results" / "sample_level_certificate_full_sweep_audit.json",
    ROOT / "paper1" / "results" / "sample_level_certificate_full_sweep_audit.csv",
    ROOT / "paper1" / "results" / "sample_level_certificate_full_sweep_samples.csv",
    ROOT / "paper1" / "results" / "sample_level_certificate_full_sweep_summary.csv",
    ROOT / "paper1" / "results" / "sample_level_certificate_recovery_alignment.csv",
    ROOT / "paper1" / "results" / "sample_level_event_rate_wilson_ci.csv",
    ROOT / "paper1" / "results" / "gaussian_sensitivity_audit.json",
    ROOT / "paper1" / "results" / "gaussian_sensitivity_audit.csv",
    ROOT / "paper1" / "results" / "gaussian_sensitivity_summary.csv",
    ROOT / "paper1" / "results" / "jvp_hutchinson_sensitivity_audit.json",
    ROOT / "paper1" / "results" / "jvp_hutchinson_sensitivity_audit.csv",
    ROOT / "paper1" / "results" / "jvp_hutchinson_sensitivity_summary.csv",
    ROOT / "paper1" / "results" / "remediation_phase1_smoke_v2.json",
    ROOT
    / "paper1"
    / "results"
    / "remediation_phase1_smoke_sources"
    / "acpc_pldm_tworoom_v2.json",
    ROOT
    / "paper1"
    / "results"
    / "remediation_phase1_smoke_sources"
    / "acpc_pldm_pusht_v2.json",
    ROOT
    / "paper1"
    / "results"
    / "remediation_phase1_smoke_sources"
    / "jvp_lewm_seed3072_tworoom_v2.json",
    ROOT
    / "paper1"
    / "results"
    / "remediation_phase1_smoke_sources"
    / "jvp_lewm_seed3072_pusht_v2.json",
    ROOT / "paper1" / "results" / "joint_guard_side_validation.csv",
    ROOT / "paper1" / "tables" / "table_heldout_diagnostic_validation.tex",
    ROOT / "paper1" / "tables" / "table_endpoint_atr_smpr.tex",
    ROOT / "paper1" / "tables" / "table_fixed_pool_tail_audit.tex",
    ROOT / "paper1" / "tables" / "table_sample_level_certificate_full_sweep.tex",
    ROOT / "paper1" / "tables" / "table_sample_level_event_rate_ci.tex",
    ROOT / "paper1" / "tables" / "table_sample_level_certificate_endpoint.tex",
    ROOT / "paper1" / "tables" / "table_joint_guard_side_validation.tex",
    ROOT / "paper1" / "tables" / "table_gaussian_sensitivity_audit.tex",
    ROOT / "paper1" / "tables" / "table_jvp_hutchinson_sensitivity_audit.tex",
    ROOT / "paper1" / "tables" / "table_theory_evidence_map.tex",
    ROOT / "paper1" / "tables" / "table_threshold_quantile_sensitivity.tex",
    ROOT / "paper1" / "scripts" / "build_diagnostic_manifest.py",
    ROOT / "paper1" / "scripts" / "build_cross_stressor_external_validation.py",
    ROOT / "paper1" / "scripts" / "build_full_sweep_diagnostics.py",
    ROOT / "paper1" / "scripts" / "fixed_pool_tail_audit.py",
    ROOT / "paper1" / "scripts" / "heldout_diagnostic_validation.py",
    ROOT / "paper1" / "scripts" / "plot_full_sweep_diagnostics.py",
    ROOT / "paper1" / "scripts" / "plot_endpoint_atr_smpr.py",
    ROOT / "paper1" / "scripts" / "plot_fixed_pool_event_rates.py",
    ROOT / "paper1" / "scripts" / "plot_gaussian_sensitivity_mechanism.py",
    ROOT / "paper1" / "scripts" / "threshold_quantile_sensitivity.py",
    ROOT / "paper1" / "scripts" / "utils_paper1_io.py",
    ROOT / "paper1" / "scripts" / "sample_level_certificate_summary.py",
    ROOT / "paper1" / "scripts" / "full_sweep_sample_level_certificate_summary.py",
    ROOT / "paper1" / "scripts" / "sample_level_event_rate_ci.py",
    ROOT / "paper1" / "scripts" / "joint_guard_side_validation.py",
    ROOT / "tools" / "paper1_sample_level_certificate.py",
    ROOT / "tools" / "paper1_gaussian_sensitivity_audit.py",
    ROOT / "tools" / "paper1_jvp_hutchinson_sensitivity_audit.py",
    ROOT / "paper1" / "scripts" / "run_all_paper1_diagnostics.sh",
    ROOT / "paper1" / "scripts" / "collect_tex_figures.py",
    ROOT / "paper1" / "scripts" / "README.md",
    ROOT / "paper1" / "docs" / "codex_paper1_experiment_remediation_plan.md",
    ROOT / "paper1" / "docs" / "EXPERIMENT_REMEDIATION_STATUS_20260708.md",
    ROOT / "tools" / "paper1_radius_margin_certificate.py",
    ROOT / "tools" / "paper1_boundary_mechanism_audit.py",
    ROOT / "tools" / "paper1_diagnostic_region_validation.py",
    ROOT / "paper1" / "config" / "frozen_diagnostic_protocol_v1.json",
    ROOT / "paper1" / "config" / "frozen_diagnostic_protocol_v1.schema.json",
    ROOT / "paper1" / "results" / "frozen_external_validation_summary_v3.json",
    ROOT / "paper1" / "tables" / "table_pldm_architecture_portability.tex",
    ROOT / "paper1" / "results" / "external_validation" / "cross_stressor_fixed_rho_summary.json",
    ROOT / "paper1" / "results" / "external_validation" / "cross_stressor_fixed_rho_rows.csv",
    ROOT / "paper1" / "results" / "external_validation" / "cross_stressor_all_pairs.csv",
    ROOT / "paper1" / "results" / "external_validation" / "target_view_frozen_summary.json",
    ROOT / "paper1" / "results" / "diagnostic_baselines" / "diagnostic_baseline_all_v1.json",
    ROOT / "paper1" / "results" / "diagnostic_baselines" / "gaussian_rho_confound_summary.json",
    ROOT / "paper1" / "results" / "jvp_hutchinson_sensitivity_audit_v2.json",
    ROOT / "paper1" / "results" / "linearization_horizon_sensitivity_v1.json",
    ROOT / "paper1" / "results" / "fixed_pool_candidatewise_certificate_summary.json",
    ROOT / "assets" / "paper1_data" / "smpr_sensitivity_v2.json",
    ROOT / "assets" / "paper1_data" / "smpr_controls_v2.json",
    ROOT / "assets" / "paper1_data" / "smpr_oracle_guard_v2.json",
    ROOT / "assets" / "paper1_figs" / "fig_diagnostic_baseline_external.png",
    ROOT / "assets" / "paper1_figs" / "fig_fixed_pool_certificate_calibration.png",
    ROOT / "assets" / "paper1_figs" / "fig_linearization_calibration.png",
    ROOT / "assets" / "paper1_figs" / "fig_smpr_radius_margin_decomposition.png",
    ROOT / "paper1" / "tables" / "table_cross_stressor_paired_change.tex",
    ROOT / "paper1" / "tables" / "table_cross_stressor_robustness_audit.tex",
    ROOT / "paper1" / "tables" / "table_fixed_pool_certificate_coverage.tex",
    ROOT / "paper1" / "tables" / "table_linearization_calibration.tex",
    ROOT / "paper1" / "tables" / "table_horizon_quantile_sensitivity.tex",
    ROOT / "paper1" / "tables" / "table_smpr_sensitivity.tex",
    ROOT / "paper1" / "tables" / "table_smpr_controls.tex",
    ROOT / "tools" / "paper1_linearization_horizon_audit.py",
    ROOT / "tests" / "test_paper1_linearization_horizon_audit.py",
    ROOT / "tests" / "test_paper1_cross_stressor_external_validation.py",
    ROOT / "DATA_MANIFEST.md",
]


LEGACY_REQUIRED_MAIN_TEXT_SNIPPETS = [
    "ACPC Tail Risk (ATR)",
    "Selective Margin Pass Rate (SMPR)",
    "The reported diagnostic uses two metrics matched to this radius--margin logic",
    "ATR and SMPR are empirical diagnostics aligned with the radius and margin sides, not calibrated flip-probability bounds",
    "fixed empirical reporting choice, not a theoretical constant",
    "The same guard can be posed over state--action pairs",
    "Encoder geometry remains an indispensable first-stage risk signal",
    "raw encoder distance alone is not a complete robustness criterion",
    "It need not reduce the rollout-side Jacobian uniformly",
    "lower composed encoder--rollout response to actual noise-induced perturbations",
    "Low ATR without high SMPR is not interpreted as robustness",
    "Full-sequence Gaussian noise training produces broad, task-dependent recovery bands",
    "Because \Cref{fig:sweep} already aggregates the full sweep across three training seeds",
    "fig:endpoint-atr-smpr",
    "fig_fixed_pool_event_rates.png",
    "fig_gaussian_sensitivity_main.png",
    "Mixed blur/resize outcomes delimit the matched-Gaussian scope",
    "raw no-noise $\\to$ noise-trained diagnostic values under the row stressor",
    "We treat this as bounded behavior outside the matched Gaussian setting",
    "These rows therefore support only a bounded severe-stressor association rather than a general perturbation-transfer claim",
    "programmatic task-state proxy labels",
    "The joint fixed-pool top-1 flip guard mitigates this proxy-label limitation",
    "does not replace stronger oracle-level contact, topology, action-value, or cost-to-go semantics",
    "closest 35\% state-distance neighborhood",
    "Hand-labeled or simulator-derived contact, topology, action-value, or cost-to-go labels remain future validation",
    "These proofs support the diagnostic use of ATR and SMPR",
    "Additional Gaussian Evaluation Tables",
    "These tables report the full observation-only Gaussian evaluation columns available",
    "Future methods can turn ATR/SMPR into objectives",
    "fixed-pool radius--margin diagnostic bound",
    "Predictive tubes and planner margins",
    "Fixed-pool radius--margin bound",
    "Matched-perturbation diagnostic region",
    "Local Gaussian ACPC radius quantile",
    "Planner-side radius--margin audit",
    "mechanism proxy, not a calibrated planner-margin bound",
    "finite-sample empirical fixed-pool risk audit",
    "lower normalized ATR and higher SMPR",
    "Planner-side top-1 disagreement is separated",
    "Qualitative ACPC neighborhood view",
    "fig_full_sweep_planner_guard.png",
    "fig_jvp_trace_decomposition_heatmap.png",
    "Those q10/q95 gaps remain negative",
    "aggregate grid-point F1 or interval IoU is not used as the primary validation criterion",
    "Full-sweep and held-out validation",
    "Across all $4\\times3\\times9=108$",
    "mean absolute recovery-onset error $0.007$",
    "leave-one-task-out validation",
    "Threshold sensitivity is reported",
    "not as universal checkpoint rankers",
    "Boundary-aware interpretation of the fixed-pool radius--margin proxy",
    "Fixed-pool top-1 agreement analysis derived from the measured fixed-pool flip rate",
    "Diagnostic Validation Details",
    "Local Sensitivity Details",
    "Boundary Stressors",
    "Reproducibility",
    "The separate sample-level recomputation evaluates the sufficient event directly over the fixed 65-candidate pool for all 108 rows",
    "Those q10/q95 gaps remain negative",
    "median cert-pass rises from $0.06$",
    "Local Gaussian sensitivity explains ATR contraction",
    "endpoint/base reductions under both local estimators",
    "using 100 sampled sequences and 5 noise draws per small $\sigma$ and checkpoint",
    "an exact-autograd JVP/Hutchinson analysis estimates raw Frobenius traces",
    "the same weighted-stacked rollout map",
    "one canonical weighted-stacked horizon radius per anchor",
    "multiple noise draws are first averaged within the anchor",
    "it is not ATR and is not used as the canonical horizon-radius statistic",
    "The relative isotropic gain can exceed one",
    "using 100 sampled sequences and 8 Rademacher probes per checkpoint",
    "The two estimators are not expected to match numerically",
    "not as a cross-task scale or a shared threshold",
    "Complementary finite-difference and exact-JVP/Hutchinson analyses",
    "maps each theoretical object to its empirical evidence and limitation",
    "the decomposition attributes the composed-trace reduction mainly to encoder-side sensitivity reduction",
    "rollout-side trace is task-dependent rather than uniformly smaller",
    "tighter post-rollout feature clouds measure the composed response",
    "not claim a standalone predictor-Jacobian repair",
    "observed top-1 flips conditioned on cert-pass are zero",
    "rather than calibrated probabilities",
    "SMPR and fixed-pool top-1 flip are guard-side criteria and are not standalone robustness metrics",
    "unavailable ATR/SMPR tail variants are reported as unavailable rather than inferred",
    "q10/q95 rule is too conservative for the current fixed-pool cost scale",
    "$\\beta_{\\mathrm{plan}}$ and $\\beta_{\\mathrm{disc}}$ name empirical failure components rather than calibrated probabilities",
    "The radius--margin bound is fixed-pool and matched-perturbation only",
    "adaptive CEM resampling, repeated replanning, or environment-feedback trajectory guarantees",
    "The Gaussian sensitivity analyses are local: finite-difference slopes and exact-JVP/Hutchinson trace estimates do not provide a global robustness or closed-loop guarantee",
    "SMPR is only a guard-side component of the joint diagnostic and uses programmatic proxy labels",
    "fixed-pool top-1 flip guard evaluates planning consistency but does not replace stronger semantic labels",
    "radius--margin diagnostic theory for fixed-checkpoint Gaussian robustness",
    "Radius--margin parameter interpretation",
    "candidate count is $K=65$",
    "A q90 summary descriptively leaves 10\\%",
    "not as a calibrated probability guarantee",
    "65\\times0.1=6.5",
    "tab:appendix-radius-margin-params",
    "Across the full Gaussian training sweep, recovered rows occupy low-ATR/high-SMPR regions",
    "full-sweep fixed-pool event-rate recomputation links the radius--margin mechanism to candidate stability",
    "The separate sample-level recomputation in \Cref{tab:sample-level-certificate-full-sweep} provides q10/q95 gaps and event rates",
    "q10/q95 gaps remain negative, so the analysis supports the mechanism rather than a calibrated planner-margin bound",
    "observed top-1 flips conditioned on cert-pass are zero",
    "paired event-rate calibration",
    "\\hat p_{\\mathrm{flip}\\mid\\mathrm{cert}}",
    "Fixed-pool event-rate audit",
    "maps each theoretical object to its empirical evidence and limitation",
    "The sufficient-event interpretation is sample-level",
    "event rates remain informative even though the distribution-level q10/q95 gap is negative",
]

# Public-v1 gates are structural and claim-oriented.  The longer list above is
# retained only to document the pre-remediation wording contract.
REQUIRED_MAIN_TEXT_SNIPPETS = [
    "This is a diagnostic study of frozen checkpoints, not a new robust-training method",
    "same-state visual perturbation",
    "Common-future error-drift bound",
    "Selective Margin Pass Rate (SMPR)",
    "not a candidate-distribution probability",
    "SMPR is designed to detect gross collapse",
    "The rule requires the reference and does not imply",
    "raw thresholds are not assumed to transfer across model architectures",
    "adaptive result is conditional on pool alignment",
    "Evaluation seeds are conditional measurement replicates",
    "No blur- or resize-specific adjustment is made",
    "not one numerical threshold for every task or model family",
    "They do not establish an absolute robustness classifier",
    "t-SNE does not preserve metric geometry",
    "not an independent statistical success count",
    "does not rank encoder shift",
]

MAIN_TEXT_FIGURES = {
    "fig_full_sweep_diagnostics.pdf",
    "fig_future_drift_three_seed_v1.pdf",
    "fig_acpc_planner_evidence.pdf",
    "fig_cross_task_atr_smpr_source_coverage_v1.pdf",
    "fig_cross_stressor_selective_transfer_v1.pdf",
}

APPENDIX_FIGURES = {
    "fig_acpc_basin_tsne.png",
    "fig_gaussian_sensitivity_main.png",
}




LEGACY_FORBIDDEN_SNIPPETS = [
    "H8 predictor",
    "H=8 predictor",
    "8-step predictor basin",
    "ACPC rollout $R_F$",
    "R_E",
    "R_F",
    "PCC",
    "CRA",
    "MAF",
    "CEM trace",
    "CEMSolver",
    "ID probe",
    "effective rank",
    "transition-resolution",
    "Phase-0",
    "selector",
    "DATA_MANIFEST",
    "manifest",
    "release package",
    "JSON",
    "hash",
    "rendering",
    "scripts",
    "selective_contraction",
    "fig:selective",
    "tab:acpc-basin",
    "tab:acpc-downstream",
    "tab:diag-base",
    "tab:margin-flip",
    "tab:selector",
    "tab:cem",
    "appendix-phase0",
    "appendix-selector",
    "appendix-cem",
    "appendix-diagnostic-framework",
    "appendix-pldm",
    "appendix-A-atlas",
    "public repository",
    "data manifest",
    "coarse collapse",
    "The data reject",
    "bought by",
    "small CEM trace audit",
    "point-optimal std prediction",
    "heteroscedastic",
    "Heteroscedastic",
    "target-view",
    "Target-view",
    "Target-View",
    "clean-target denoising",
    "negative ablation",
]

FORBIDDEN_SNIPPETS = [
    "we introduce action-conditioned predictive consistency",
    "universal robustness predictor",
    "is a universal checkpoint selector",
    "general corruption transfer theorem",
    "three independent PLDM training seeds",
    "flip|cert=0 proves",
    "kappa_relative_isotropic is bounded",
    "ATM reproduction",
]


EXPECTED_TASKS = {"TwoRoom", "PushT", "Reacher", "Cube"}
EXPECTED_CONFIGS = {
    "0.0",
    "0.01",
    "0.02",
    "0.03",
    "0.04",
    "0.05",
    "0.06",
    "0.07",
    "0.08",
}
REQUIRED_METRICS = {
    "clean",
    "pixels_std0.05",
    "pixels_std0.08",
    "pixels_goal_std0.05",
    "pixels_goal_std0.08",
}
THREE_SEED_SWEEP_METRICS = {
    "clean",
    "obs_sigma_0.03",
    "obs_sigma_0.05",
    "obs_sigma_0.08",
    "obs_goal_sigma_0.08",
}
REQUIRED_DIAG_TASKS = EXPECTED_TASKS
EXPECTED_METHODS = {"LeWM", "PLDM"}
FROZEN_PROTOCOL_SHA256 = "edcb801c3da388e673c9b55d706a558aa01da7a281fc151e52e1cda566045a21"
PAIRED_MULTISEVERITY_PROTOCOL_SHA256 = "6712b4f595444d751d9c327262c288e37dbd80be7ddde9bb4fd336ed41119622"
PAIRED_MULTISEVERITY_ADDENDUM_SHA256 = "70ca8cb9a361f144ca047235ae5844e0859394dd350cb021eb8c5720845d44c2"
PAIRED_MULTISEVERITY_ADDENDUM_V2_SHA256 = "ac89c6c69ae67e123c90205a9de532f9a0bb9709ad91c5404c1f43dc23ea5afb"
PAIRED_MULTISEVERITY_REFERENCE_SMOKE_SHA256 = "6c7622ae2f78899b5e2f8e6ea5f2c4ae6455ae342aef1f64bfa080b8ced4a8e1"
PAIRED_MULTISEVERITY_SMPR_SMOKE_SHA256 = "eb41ff0d6a23db0e15ea5f48540f91f5d834831d13dff7e6bb8ba8c6fbcffdbe"
PUBLIC_V1_ARTIFACT_HASHES = {
    "paper1/config/frozen_diagnostic_protocol_v1.json": FROZEN_PROTOCOL_SHA256,
    "paper1/results/frozen_external_validation_summary_v3.json": "ec485a7026c1d2ff80295f4dc85dd3753ca12f2ede7d7c0137a13796070dfeba",
    "paper1/tables/table_pldm_architecture_portability.tex": "8c4fda0abec11a777249422b08ab7fb3ced11ee5222962f28d0ca6ec4f73309e",
    "paper1/results/external_validation/cross_stressor_fixed_rho_summary.json": "94077f772e8dd7641b47e161a17d4ec67cea695dc044cb9a0229857efc157453",
    "paper1/results/external_validation/target_view_frozen_summary.json": "dba255daf282d1dbea7a102839e054cdd39b159a08a9ea9b1d3def7767477870",
    "paper1/results/diagnostic_baselines/diagnostic_baseline_all_v1.json": "df43cfd80b0387bde31426a37445149646a247724c1b2dd61f801a97d6c4f3c8",
    "paper1/results/diagnostic_baselines/gaussian_rho_confound_summary.json": "3079d357d7dcca2643dc0a4ef9bb3297bf1de49cfcfae51ae632bdc272ed3591",
    "paper1/results/jvp_hutchinson_sensitivity_audit_v2.json": "50cd24027772129a1d594299ec50c2df908894f9a32f3790f43e2b5273936cc5",
    "paper1/results/linearization_horizon_sensitivity_v1.json": "4697d6ac006348803b3597af15f276a4c0233b4c65081fd13164e7f5629e5ee1",
    "paper1/results/fixed_pool_candidatewise_certificate_summary.json": "ccd8c0e35fa18cd4b1af4b6f43ed70af64ac21b97abfd4cf73e3cb69789e67fe",
    "assets/paper1_data/smpr_sensitivity_v2.json": "c61df36c5a3eeeed0749f7f6f4d84dd50a91ec3a60a643ad2097fc4cbe54b5c8",
    "assets/paper1_data/smpr_controls_v2.json": "55a53c5e8036bcca2e8be82186bbad665531e1cefc7a5a5a8045c4313d68cdf2",
    "assets/paper1_data/smpr_oracle_guard_v2.json": "1224514237a958121e9e5a7d26515d98cf5c2bf59017c65060a17ba1ccd31203",
}
EXPECTED_BLUR_CONDITIONS = {
    f"{scope}_blur_ks{kernel}"
    for scope in ("pixels", "goal", "pixels_goal")
    for kernel in (3, 7, 11, 15)
}
EXPECTED_PLDM_FULL_DIAG_METRICS = {
    "clean_effective_rank",
    "clean_nn_cos_dist_median",
    "transition_resolution_ratio_l2",
    "transition_resolution_ratio_cos",
    "id_probe_r2",
    "action_mean_pred_shift_norm",
    "predictor_target_to_nn_cos_ratio_at_max_std",
    "predictor_rollout_T8_l2",
}
EXPECTED_ACPC_PHASE0_METRICS = {
    "encoder_shift_to_nn_l2",
    "acpc_1_norm_by_transition",
    "acpc_h_norm_by_transition",
    "pcc_abs_median",
    "pcc_abs_p90",
    "cra_spearman_mean",
    "elite_overlap_mean",
    "maf_flip_rate",
    "adm_l2_median",
    "sprr",
}
EXPECTED_BOOTSTRAP_SCOPES = {"within_lewm", "within_pldm", "joint"}
EXPECTED_BOOTSTRAP_METRICS = {"frag", "drift"}
EXPECTED_ACPC_BASIN_CORRUPTIONS = {round(i / 100, 2) for i in range(1, 9)}
REQUIRED_ACPC_BASIN_FIELDS = {
    "pixels_std0.08_success",
    "pixels_goal_std0.08_success",
    "corruption_drop",
    "pixels_goal_corruption_drop",
    "encoder_view_pair_l2_norm_by_nn",
    "pred_view_pair_l2_norm_by_transition",
    "basin_contraction_pair_norm",
    "encoder_to_clean_l2_norm_by_nn_median",
    "pred_to_clean_l2_norm_by_transition_median",
    "basin_contraction_to_clean_norm_median",
}
TOL = 1e-9


def fail(msg: str) -> None:
    raise AssertionError(msg)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_strict_json(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant {value!r}")

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=reject_constant,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)} is not strict JSON: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.relative_to(ROOT)} must contain a top-level object")
    return payload


def check_artifacts() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_ARTIFACTS if not path.exists()]
    if missing:
        fail(f"Missing release artifacts: {', '.join(missing)}")


def check_paired_multiseverity_protocol() -> None:
    protocol_rel = "paper1/config/paired_multiseverity_protocol_v1.json"
    protocol_path = ROOT / protocol_rel
    got_hash = _sha256_file(protocol_path)
    if got_hash != PAIRED_MULTISEVERITY_PROTOCOL_SHA256:
        fail(
            "paired multi-severity protocol hash changed: "
            f"got {got_hash}, want {PAIRED_MULTISEVERITY_PROTOCOL_SHA256}"
        )

    sidecar = (
        ROOT / "paper1/config/paired_multiseverity_protocol_v1.sha256"
    ).read_text(encoding="utf-8").split()
    if sidecar != [PAIRED_MULTISEVERITY_PROTOCOL_SHA256, protocol_rel]:
        fail("paired multi-severity protocol hash sidecar changed")

    protocol = _load_strict_json(protocol_path)
    scope = protocol.get("scope", {})
    stressors = protocol.get("stressors", {})
    diagnostic = protocol.get("diagnostic", {})
    analysis = protocol.get("primary_analysis", {})
    execution = protocol.get("execution", {})
    if (
        protocol.get("schema_version") != "paper1-paired-multiseverity-protocol-1.0"
        or protocol.get("status") != "frozen_pre_execution"
        or scope.get("primary_model_family") != "LeWM"
        or scope.get("training_seeds") != [3072, 3073, 3074]
        or scope.get("tasks") != ["TwoRoom", "PushT", "Reacher", "Cube"]
    ):
        fail("paired multi-severity frozen scope changed")
    if (
        stressors.get("gaussian_blur", {}).get("primary_nonidentity") != [7, 11, 15]
        or stressors.get("resize", {}).get("primary_nonidentity")
        != [0.75, 0.5, 0.25]
    ):
        fail("paired multi-severity severity grid changed")
    expected_pairs = (
        len(scope["training_seeds"])
        * len(scope["tasks"])
        * len(stressors)
        * 3
    )
    if analysis.get("expected_pairs") != expected_pairs or expected_pairs != 72:
        fail("paired multi-severity 72-pair count contract changed")
    if (
        diagnostic.get("decision_threshold") != 0
        or diagnostic.get("threshold_search_allowed") is not False
        or diagnostic.get("severity_search_allowed") is not False
        or analysis.get("block_count") != 12
        or analysis.get("block_bootstrap_seed") != 20260712
        or "2^12" not in analysis.get("exact_randomization", "")
    ):
        fail("paired multi-severity preregistered analysis rule changed")
    if (
        execution.get("max_concurrent_eval_jobs") != 1
        or execution.get("max_concurrent_diagnostic_jobs") != 1
        or execution.get("smoke_first", {}).get("severity") != 7
    ):
        fail("paired multi-severity bounded serial execution contract changed")

    source_paths = protocol.get("source_paths", {})
    source_hashes = protocol.get("source_hashes", {})
    if source_paths.keys() != source_hashes.keys():
        fail("paired multi-severity source hash map is incomplete")
    for name, rel in source_paths.items():
        if _sha256_file(ROOT / rel) != source_hashes[name]:
            fail(f"paired multi-severity bound source changed: {name}")

    addendum_rel = "paper1/config/paired_multiseverity_execution_addendum_v1.json"
    addendum_path = ROOT / addendum_rel
    if _sha256_file(addendum_path) != PAIRED_MULTISEVERITY_ADDENDUM_SHA256:
        fail("paired multi-severity execution addendum hash changed")
    addendum_sidecar = (
        ROOT / "paper1/config/paired_multiseverity_execution_addendum_v1.sha256"
    ).read_text(encoding="utf-8").split()
    if addendum_sidecar != [PAIRED_MULTISEVERITY_ADDENDUM_SHA256, addendum_rel]:
        fail("paired multi-severity addendum hash sidecar changed")
    addendum = _load_strict_json(addendum_path)
    disclosure = addendum.get("non_blind_disclosure", {})
    revision = addendum.get("pre_smpr_revision", {})
    science = addendum.get("scientific_contract", {})
    if (
        addendum.get("schema_version")
        != "paper1-paired-multiseverity-execution-addendum-1.0"
        or addendum.get("status")
        != "frozen_after_adapter_validation_fix_before_smpr"
        or addendum.get("parent_protocol", {}).get("sha256")
        != PAIRED_MULTISEVERITY_PROTOCOL_SHA256
        or disclosure.get("created_after_behavior_and_atr_smoke") is not True
        or disclosure.get("behavior_outcomes_were_inspected_before_this_addendum")
        is not True
        or disclosure.get("analysis_threshold_or_severity_changed") is not False
        or revision.get("reference_or_smpr_output_created_before_fix") is not False
        or science.get("decision_threshold") != 0
        or science.get("threshold_search_allowed") is not False
        or science.get("severity_search_allowed") is not False
    ):
        fail("paired multi-severity addendum disclosure/scientific boundary changed")
    for section in ("execution_only_sources", "bound_measurement_sources"):
        for name, entry in addendum.get(section, {}).items():
            if _sha256_file(ROOT / entry["path"]) != entry["sha256"]:
                fail(f"paired multi-severity addendum source changed: {name}")
    disclosed_artifacts = {
        "atr_smoke": (
            "paper1/results/multiseverity_v1/raw/lewm_seed3072/"
            "gaussian_blur_ks7/acpc_tworoom_v2.json"
        ),
        "behavior_manifest_reference": (
            "paper1/results/multiseverity_v1/manifests/"
            "behavior_s3072_tworoom_std0p0_gaussian_blur.json"
        ),
        "behavior_manifest_endpoint": (
            "paper1/results/multiseverity_v1/manifests/"
            "behavior_s3072_tworoom_std0p08_gaussian_blur.json"
        ),
    }
    disclosed_hashes = disclosure.get("pre_addendum_artifact_hashes", {})
    for name, rel in disclosed_artifacts.items():
        if _sha256_file(ROOT / rel) != disclosed_hashes.get(name):
            fail(f"paired multi-severity pre-addendum disclosure hash changed: {name}")

    addendum_v2_rel = "paper1/config/paired_multiseverity_execution_addendum_v2.json"
    addendum_v2_path = ROOT / addendum_v2_rel
    if _sha256_file(addendum_v2_path) != PAIRED_MULTISEVERITY_ADDENDUM_V2_SHA256:
        fail("paired multi-severity execution addendum v2 hash changed")
    addendum_v2_sidecar = (
        ROOT / "paper1/config/paired_multiseverity_execution_addendum_v2.sha256"
    ).read_text(encoding="utf-8").split()
    if addendum_v2_sidecar != [
        PAIRED_MULTISEVERITY_ADDENDUM_V2_SHA256,
        addendum_v2_rel,
    ]:
        fail("paired multi-severity addendum v2 hash sidecar changed")
    addendum_v2 = _load_strict_json(addendum_v2_path)
    failure_v2 = addendum_v2.get("failure_disclosure", {})
    unchanged_v2 = addendum_v2.get("scientific_contract_unchanged", {})
    if (
        addendum_v2.get("schema_version")
        != "paper1-paired-multiseverity-execution-addendum-2.0"
        or addendum_v2.get("parent_protocol", {}).get("sha256")
        != PAIRED_MULTISEVERITY_PROTOCOL_SHA256
        or addendum_v2.get("parent_execution_addendum", {}).get("sha256")
        != PAIRED_MULTISEVERITY_ADDENDUM_SHA256
        or failure_v2.get("reference_binding_failed") is not True
        or failure_v2.get("threshold_or_severity_changed") is not False
        or failure_v2.get("v1_outputs_before_failure")
        != {
            "valid_tworoom_shards": 4,
            "unmatched_pusht_shards": 1,
            "remaining_unattempted_shards": 43,
        }
        or unchanged_v2.get("decision_threshold") != 0
        or unchanged_v2.get("threshold_search_allowed") is not False
        or unchanged_v2.get("severity_search_allowed") is not False
    ):
        fail("paired multi-severity addendum v2 disclosure/scientific boundary changed")
    for section in ("execution_sources", "bound_measurement_sources"):
        for name, entry in addendum_v2.get(section, {}).items():
            if _sha256_file(ROOT / entry["path"]) != entry["sha256"]:
                fail(f"paired multi-severity addendum v2 source changed: {name}")

    v1_archive_dir = (
        ROOT
        / "paper1/results/multiseverity_v1/raw/lewm_seed3072/gaussian_blur_ks7"
    )
    archived_tworoom = sorted(
        v1_archive_dir.glob("smpr_tworoom_v2.json.pre_v2_or_invalid_*")
    )
    archived_pusht = sorted(
        v1_archive_dir.glob("smpr_pusht_v2.json.pre_v2_or_invalid_*")
    )
    if (
        len(archived_tworoom) != 1
        or len(archived_pusht) != 1
        or _sha256_file(archived_tworoom[0])
        != "73da06004db247d38d5330b51bc55d348529c836547065dc334010b791ca5bc3"
        or _sha256_file(archived_pusht[0])
        != "a15b7292d5b7c15d293729bfdd7c1eabf6e2c516153e07289079fca3ba5f4762"
    ):
        fail("paired multi-severity v1 SMPR failure archives changed")

    behavior = (ROOT / execution["behavior_runner"]).read_text(encoding="utf-8")
    atr = (ROOT / execution["atr_runner"]).read_text(encoding="utf-8")
    for token in (
        "plan|smoke|full",
        "--only-missing",
        "eval_max_concurrency=1",
        "eval_resume=1",
        "eval_save_video=0",
        "timeout --signal=TERM --kill-after=60s",
        "frozen protocol hash mismatch",
    ):
        if token not in behavior:
            fail(f"multi-severity behavior runner lost control: {token}")
    for token in (
        "valid_shard",
        "status_counts",
        "timeout --signal=TERM --kill-after=60s",
        "PAPER1_DIAGNOSTIC_THREADS",
        "frozen protocol hash mismatch",
    ):
        if token not in atr:
            fail(f"multi-severity ATR runner lost control: {token}")

    reference_smoke = (
        ROOT
        / "paper1/results/multiseverity_v1/reference/lewm_seed3072"
        / "gaussian_blur_ks7/acpc_tworoom_horizon_v2_checkpoint_bound.json"
    )
    smpr_smoke_path = (
        ROOT
        / "paper1/results/multiseverity_v1/raw/lewm_seed3072"
        / "gaussian_blur_ks7/smpr_tworoom_v2.json"
    )
    if _sha256_file(reference_smoke) != PAIRED_MULTISEVERITY_REFERENCE_SMOKE_SHA256:
        fail("paired multi-severity ATR reference smoke hash changed")
    if _sha256_file(smpr_smoke_path) != PAIRED_MULTISEVERITY_SMPR_SMOKE_SHA256:
        fail("paired multi-severity SMPR smoke hash changed")
    smpr_smoke = _load_strict_json(smpr_smoke_path)
    smpr_meta = smpr_smoke.get("metadata", {})
    smpr_rows = smpr_smoke.get("rows", [])
    if (
        smpr_meta.get("status") != "complete"
        or smpr_meta.get("status_counts") != {"ok": 2}
        or smpr_meta.get("missing_rows") != []
        or smpr_meta.get("errors") != []
        or len(smpr_rows) != 2
    ):
        fail("paired multi-severity SMPR smoke is incomplete")
    smpr_by_std = {str(row.get("std_key")): row for row in smpr_rows}
    if set(smpr_by_std) != {"0.0", "0.08"}:
        fail("paired multi-severity SMPR smoke checkpoint pair changed")
    expected_smoke = {
        "0.0": (2.0391573905944824, 0.016393441706895828),
        "0.08": (0.6844772100448608, 0.9672130346298218),
    }
    for std_key, (expected_atr, expected_smpr) in expected_smoke.items():
        row = smpr_by_std[std_key]
        if (
            row.get("status") != "ok"
            or row.get("atr_reference_match") is not True
            or row.get("atr_reference_abs_error") != 0
            or not math.isclose(row["same_state_tube_radius"], expected_atr, abs_tol=1e-12)
            or not math.isclose(row["smpr"], expected_smpr, abs_tol=1e-12)
        ):
            fail(f"paired multi-severity SMPR smoke row changed: {std_key}")
    base_protocol = _load_strict_json(ROOT / "paper1/config/frozen_diagnostic_protocol_v1.json")
    tau_atr = float(base_protocol["tau_atr"])
    tau_smpr = float(base_protocol["tau_smpr"])
    joint_scores = {}
    for std_key, row in smpr_by_std.items():
        atr_margin = (tau_atr - float(row["same_state_tube_radius"])) / abs(tau_atr)
        smpr_margin = (float(row["smpr"]) - tau_smpr) / abs(tau_smpr)
        joint_scores[std_key] = min(atr_margin, smpr_margin)
    if not math.isclose(
        joint_scores["0.08"] - joint_scores["0.0"],
        0.9999999804090585,
        abs_tol=1e-12,
    ):
        fail("paired multi-severity smoke delta joint score changed")

    smpr_runner = (ROOT / "paper1/scripts/run_paired_multiseverity_smpr.sh").read_text(
        encoding="utf-8"
    )
    for token in (
        "valid_reference",
        "valid_smpr",
        "atr_reference_match == true",
        "timeout --signal=TERM --kill-after=60s",
        'verify_frozen_file "$addendum"',
    ):
        if token not in smpr_runner:
            fail(f"multi-severity SMPR runner lost control: {token}")

    smpr_runner_v2 = (
        ROOT / "paper1/scripts/run_paired_multiseverity_smpr_v2.sh"
    ).read_text(encoding="utf-8")
    for token in (
        'acpc_${task_slug}_horizon_v2_checkpoint_bound.json',
        ".metadata.task == $task",
        ".metadata.source_sha256 == $raw_sha",
        ".metadata.source_hashes.reference_atr == $reference_sha",
        ".atr_reference_match == true",
        'verify_frozen_file "$addendum_v2"',
    ):
        if token not in smpr_runner_v2:
            fail(f"multi-severity SMPR v2 runner lost control: {token}")

    manifest = _load_strict_json(ROOT / "paper1/results/diagnostic_manifest.json")
    prospective = manifest.get("prospective_multiseverity_extension", {})
    if prospective != {
        "completed_primary_pairs": 0,
        "evidence_status": "protocol-only; not public-v1 completed evidence",
        "execution_addendum_sha256": PAIRED_MULTISEVERITY_ADDENDUM_V2_SHA256,
        "execution_addendum_source": addendum_v2_rel,
        "expected_primary_pairs": 72,
        "parent_execution_addendum_sha256": PAIRED_MULTISEVERITY_ADDENDUM_SHA256,
        "parent_execution_addendum_source": addendum_rel,
        "protocol_sha256": PAIRED_MULTISEVERITY_PROTOCOL_SHA256,
        "protocol_source": protocol_rel,
        "smoke_validation": {
            "completed_behavior_atr_smpr_triplets": 1,
            "primary_claim_eligible": False,
            "scope": "LeWM seed3072 TwoRoom gaussian_blur kernel_size=7",
            "zero_rule_direction_agreement": True,
        },
        "status": "frozen_protocol_with_v2_task_bound_smoke",
        "v1_reference_path_failure_disclosed": True,
    }:
        fail("diagnostic manifest misstates prospective multi-severity status")


def check_forbidden_text() -> None:
    hits: list[str] = []
    for path in RELEASE_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in FORBIDDEN_SNIPPETS:
            if snippet in text:
                hits.append(f"{path.relative_to(ROOT)} contains forbidden snippet: {snippet!r}")
    main_tex = (ROOT / "paper1" / "main.tex").read_text(encoding="utf-8")
    normalized_main_tex = " ".join(main_tex.split())
    paper_facing_files = [ROOT / "paper1" / "main.tex"] + sorted((ROOT / "paper1" / "tables").glob("table_*.tex"))
    top_conference_forbidden = [
        "Remediation audit tables",
        "Bounded unseen-stressor check",
        "Bounded unseen-stressor score check",
        "Gaussian sensitivity audits",
        "Finite-difference Gaussian sensitivity audit",
        "Fixed-pool top-1 agreement audit",
        "Retained-summary fixed-pool top-1 audit",
        "Full-sweep sample-level fixed-pool event-rate audit",
        "The audit uses exact autograd JVPs",
        "held-out seed/task audits",
        "joint ATR-plus-guard audits",
        "unseen-stressor score checks",
        "training-free full-sweep audit",
        "retained full-sweep ATR/SMPR artifact",
        "retained-summary overlay",
        "recorded fixed-pool summaries",
        "recorded fixed-pool flip rate",
        "sampled fixed-pool audit anchors",
    ]
    for path in paper_facing_files:
        if not path.exists():
            continue
        paper_text = path.read_text(encoding="utf-8")
        for snippet in top_conference_forbidden:
            if snippet in paper_text:
                hits.append(f"{path.relative_to(ROOT)} contains paper-facing internal-review wording: {snippet!r}")
    main_forbidden = [
        "paper-facing claim",
        "Scope of this arXiv version",
        "complete code and data",
        "three evaluation seeds are independent training seeds",
        "cert-pass zero flips provide independent empirical evidence",
        "SMPR establishes oracle-level semantic sufficiency",
        "long-horizon action consistency is empirically necessary",
    ]
    for snippet in main_forbidden:
        if snippet in main_tex:
            hits.append(f"paper1/main.tex contains retired main-text snippet: {snippet!r}")
    for snippet in REQUIRED_MAIN_TEXT_SNIPPETS:
        if snippet not in normalized_main_tex:
            hits.append(f"paper1/main.tex missing required scope-boundary snippet: {snippet!r}")
    if hits:
        fail("\n".join(hits))


def check_appendix_internal_heading_gate() -> None:
    main_tex = (ROOT / "paper1" / "main.tex").read_text(encoding="utf-8")
    marker = "\\appendix"
    if marker not in main_tex:
        fail("paper1/main.tex missing appendix marker")
    appendix = main_tex.split(marker, 1)[1]
    forbidden = ["\\paragraph{Reading.}", "\\paragraph{Reading:}"]
    hits = [snippet for snippet in forbidden if snippet in appendix]
    if hits:
        fail("Appendix contains internal Reading heading(s): " + ", ".join(hits))


def check_visual_text_structure() -> None:
    main_tex = (ROOT / "paper1" / "main.tex").read_text(encoding="utf-8")
    marker = "\\appendix"
    if marker not in main_tex:
        fail("paper1/main.tex missing appendix marker")
    body, appendix = main_tex.split(marker, 1)

    required_headings = (
        "\\subsection{Paired rollout radius}",
        "\\subsection{Common-future error drift}",
        "\\subsection{Planner flips as radius--margin events}",
        "\\subsection{Selective predictive consistency}",
        "\\subsection{Checkpoint-level diagnostic score}",
        "\\subsection{Evaluation setup}",
        "\\subsection{Planning performance under observation noise}",
        "\\subsection{Predicting error changes under visual perturbations}",
        "\\subsection{ACPC and CEM decisions}",
        "\\subsection{Cross-task threshold transfer}",
        "\\subsection{Application to PLDM}",
        "\\subsection{Transfer to blur and resize}",
    )
    for heading in required_headings:
        if heading not in body:
            fail(f"paper1/main.tex missing required structural heading: {heading}")

    retired_headings = (
        "\\subsection{Same-state predictive consistency and selective margin}",
        "\\subsection{Same-state predictive radius and selective margin}",
        "\\paragraph{Full-sweep and held-out evidence.}",
        "\\paragraph{Full-sweep and held-out evidence}",
    )
    for heading in retired_headings:
        if heading in body:
            fail(f"paper1/main.tex restored retired heading: {heading}")

    for retired_visual_phrase in ("SMPR failure", "1-\\mathrm{SMPR}"):
        if retired_visual_phrase in body:
            fail(f"main text restored the retired Figure 3 encoding: {retired_visual_phrase}")

    include_re = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    body_targets = include_re.findall(body)
    appendix_targets = include_re.findall(appendix)
    if len(body_targets) != len(set(body_targets)):
        fail(f"main text contains duplicate figure targets: {body_targets}")
    if len(appendix_targets) != len(set(appendix_targets)):
        fail(f"appendix contains duplicate figure targets: {appendix_targets}")

    if set(body_targets) != MAIN_TEXT_FIGURES:
        fail(
            "main-text figure set changed: "
            f"got {sorted(body_targets)}, want {sorted(MAIN_TEXT_FIGURES)}"
        )
    if set(appendix_targets) != APPENDIX_FIGURES:
        fail(
            "appendix figure set changed: "
            f"got {sorted(appendix_targets)}, want {sorted(APPENDIX_FIGURES)}"
        )

    for target in body_targets + appendix_targets:
        candidates = (
            ROOT / "paper1" / "figures" / target,
            ROOT / "assets" / "paper1_figs" / target,
        )
        if not any(path.is_file() for path in candidates):
            fail(f"TeX-referenced figure is missing: {target}")

    release_scripts = (
        ROOT / "paper1" / "check_arxiv_ready.sh",
        ROOT / "paper1" / "docs" / "check_blind_ready.sh",
    )
    for script in release_scripts:
        text = script.read_text(encoding="utf-8")
        if "collect_tex_figures.py" not in text:
            fail(f"{script.relative_to(ROOT)} does not collect TeX figure dependencies")
        if "tar -xzf" not in text:
            fail(f"{script.relative_to(ROOT)} does not verify its packaged source in isolation")

    paper_facing_tex = [
        ROOT / "paper1" / "main.tex",
        *sorted((ROOT / "paper1" / "tables").glob("*.tex")),
    ]
    for path in paper_facing_tex:
        text = path.read_text(encoding="utf-8")
        for token in ("Top1Agree", "std0.08", "$|$start err$|$"):
            if token in text:
                fail(f"{path.relative_to(ROOT)} contains code-like paper terminology: {token}")
        if re.search(r"\bstart(?:-boundary)? error\b", text, flags=re.IGNORECASE):
            fail(f"{path.relative_to(ROOT)} restored retired start-error terminology")

    full_sweep_plot = (ROOT / "paper1" / "scripts" / "plot_full_sweep_diagnostics.py").read_text(encoding="utf-8")
    for token in ("1-SMPR", "smpr_fail"):
        if token in full_sweep_plot:
            fail(f"Figure 3 generator restored the failure-rate encoding: {token}")
    if 'label=r"SMPR ($\\uparrow$)"' not in full_sweep_plot:
        fail("Figure 3 generator must label direct SMPR as higher-is-better")
    if not re.search(r"plt\.subplots\(1,\s*4,\s*figsize=\(6\.7,\s*2\.35\)", full_sweep_plot):
        fail("Figure 7 generator must retain the compact native-width four-across layout")

    sweep_plot = (ROOT / "tools" / "paper1_figs.py").read_text(encoding="utf-8")
    if not re.search(r"plt\.subplots\(1,\s*4,\s*figsize=\(6\.7,\s*2\.45\)", sweep_plot):
        fail("Figure 1 generator must retain the compact native-width four-across layout")

    heldout_generator = (ROOT / "paper1" / "scripts" / "heldout_diagnostic_validation.py").read_text(encoding="utf-8")
    if r"\shortstack{mean absolute\\recovery-onset error}" not in heldout_generator:
        fail("Table 2 generator must use the full recovery-onset error label")

    threshold_generator = (ROOT / "paper1" / "scripts" / "threshold_quantile_sensitivity.py").read_text(encoding="utf-8")
    if "All nine behavioral-label settings" not in threshold_generator:
        fail("Table 8 generator must retain the compact threshold-matrix summary")

    terminology_gates = {
        ROOT / "paper1" / "scripts" / "fixed_pool_tail_audit.py": ("Top1Agree",),
        ROOT / "paper1" / "scripts" / "sample_level_certificate_summary.py": ("std0.08",),
    }
    for path, forbidden_tokens in terminology_gates.items():
        text = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in text:
                fail(f"{path.relative_to(ROOT)} contains code-like paper terminology: {token}")


def approx_equal(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=TOL)


def rankdata(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def pearson(x: list[float], y: list[float]) -> float:
    mean_x = statistics.fmean(x)
    mean_y = statistics.fmean(y)
    dx = [v - mean_x for v in x]
    dy = [v - mean_y for v in y]
    denom = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    if denom <= 1e-12:
        return 0.0
    return sum(a * b for a, b in zip(dx, dy)) / denom


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(rankdata(x), rankdata(y))


def residualize_against_z(values: list[float], z: list[float]) -> list[float]:
    mean_v = statistics.fmean(values)
    mean_z = statistics.fmean(z)
    dz = [v - mean_z for v in z]
    var_z = sum(v * v for v in dz)
    if var_z <= 1e-12:
        return [0.0] * len(values)
    cov = sum((v - mean_v) * zz for v, zz in zip(values, dz))
    slope = cov / var_z
    intercept = mean_v - slope * mean_z
    return [v - (intercept + slope * zz) for v, zz in zip(values, z)]


def partial_spearman(x: list[float], y: list[float], z: list[float]) -> float | None:
    rx = rankdata(x)
    ry = rankdata(y)
    rz = rankdata(z)
    ex = residualize_against_z(rx, rz)
    ey = residualize_against_z(ry, rz)
    if max(ex) - min(ex) <= 1e-12 or max(ey) - min(ey) <= 1e-12:
        return None
    return pearson(ex, ey)


def round2(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)


def check_metric_summary(task: str, std_key: str, metric_name: str, summary: dict) -> None:
    for key in ("n", "mean", "std", "values"):
        if key not in summary:
            fail(f"{task}/{std_key}/{metric_name} missing key {key!r}")

    values = summary["values"]
    if summary["n"] != 3:
        fail(f"{task}/{std_key}/{metric_name} expected n=3, got {summary['n']}")
    if not isinstance(values, list) or len(values) != 3:
        fail(f"{task}/{std_key}/{metric_name} expected 3 seed values, got {values!r}")

    if not all(isinstance(v, (int, float)) for v in values):
        fail(f"{task}/{std_key}/{metric_name} has non-numeric seed values: {values!r}")

    mean = statistics.fmean(values)
    std = statistics.pstdev(values)
    if not approx_equal(summary["mean"], mean):
        fail(
            f"{task}/{std_key}/{metric_name} mean mismatch: "
            f"stored={summary['mean']} recomputed={mean}"
        )
    if not approx_equal(summary["std"], std):
        fail(
            f"{task}/{std_key}/{metric_name} std mismatch: "
            f"stored={summary['std']} recomputed={std}"
        )
    if not (0.0 <= summary["mean"] <= 100.0):
        fail(f"{task}/{std_key}/{metric_name} mean out of success-rate range: {summary['mean']}")
    if not (0.0 <= summary["std"] <= 100.0):
        fail(f"{task}/{std_key}/{metric_name} std out of success-rate range: {summary['std']}")


def check_canonical_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_evals_20260517.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    if set(data) != EXPECTED_TASKS:
        fail(f"Canonical tasks mismatch: expected {sorted(EXPECTED_TASKS)}, got {sorted(data)}")

    total_configs = 0
    seen_subdirs: set[str] = set()
    for task, configs in data.items():
        if set(configs) != EXPECTED_CONFIGS:
            fail(
                f"{task} config mismatch: expected {sorted(EXPECTED_CONFIGS)}, "
                f"got {sorted(configs)}"
            )
        total_configs += len(configs)
        for std_key, entry in configs.items():
            for key in ("path", "subdir", "metrics"):
                if key not in entry:
                    fail(f"{task}/{std_key} missing key {key!r}")
            subdir = entry["subdir"]
            if not isinstance(subdir, str) or not subdir:
                fail(f"{task}/{std_key} has invalid subdir: {subdir!r}")
            if subdir in seen_subdirs:
                fail(f"Duplicate canonical subdir: {subdir}")
            seen_subdirs.add(subdir)

            metrics = entry["metrics"]
            missing_metrics = REQUIRED_METRICS - set(metrics)
            if missing_metrics:
                fail(f"{task}/{std_key} missing required metrics: {sorted(missing_metrics)}")
            for metric_name in REQUIRED_METRICS:
                check_metric_summary(task, std_key, metric_name, metrics[metric_name])

    if total_configs != 36:
        fail(f"Expected 36 canonical configs, got {total_configs}")


def check_pldm_canonical_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_evals_pldm_20260522.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    if set(data) != EXPECTED_TASKS:
        fail(f"PLDM tasks mismatch: expected {sorted(EXPECTED_TASKS)}, got {sorted(data)}")

    total_configs = 0
    for task, configs in data.items():
        if set(configs) != EXPECTED_CONFIGS:
            fail(
                f"PLDM {task} config mismatch: expected {sorted(EXPECTED_CONFIGS)}, "
                f"got {sorted(configs)}"
            )
        total_configs += len(configs)
        for std_key, entry in configs.items():
            for key in ("path", "subdir", "metrics"):
                if key not in entry:
                    fail(f"PLDM {task}/{std_key} missing key {key!r}")
            metrics = entry["metrics"]
            missing_metrics = REQUIRED_METRICS - set(metrics)
            if missing_metrics:
                fail(f"PLDM {task}/{std_key} missing required metrics: {sorted(missing_metrics)}")
            for metric_name in REQUIRED_METRICS:
                check_metric_summary(f"PLDM/{task}", std_key, metric_name, metrics[metric_name])

    if total_configs != 36:
        fail(f"Expected 36 PLDM canonical configs, got {total_configs}")


def check_canonical_diagnostics_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_diagnostics_20260517.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    predictor = data.get("predictor_metrics_by_task")
    if not isinstance(predictor, dict) or set(predictor) != REQUIRED_DIAG_TASKS:
        fail(
            "canonical diagnostics predictor tasks mismatch: "
            f"expected {sorted(REQUIRED_DIAG_TASKS)}, got {sorted(predictor or {})}"
        )

    for task, configs in predictor.items():
        if set(configs) != EXPECTED_CONFIGS:
            fail(
                f"canonical diagnostics {task} config mismatch: "
                f"expected {sorted(EXPECTED_CONFIGS)}, got {sorted(configs)}"
            )
        for std_key, entry in configs.items():
            for key in (
                "subdir",
                "diagnostic_max_std",
                "predictor_target_to_nn_cos_ratio_at_max_std",
                "predictor_rollout_T8_l2_at_max_std",
            ):
                if key not in entry:
                    fail(f"canonical diagnostics {task}/{std_key} missing key {key!r}")

    rep = data.get("table3_representative_diagnostics", {})
    if set(rep.get("representative_std_by_task", {})) != REQUIRED_DIAG_TASKS:
        fail("canonical diagnostics representative std map is incomplete")
    for task, std in rep.get("representative_std_by_task", {}).items():
        if abs(float(std) - 0.08) > 1e-12:
            fail(
                "canonical diagnostics Table 3 must use the fixed high-noise "
                f"std=0.08 checkpoint for every task; got {task}={std}"
            )
    values = rep.get("values", {})
    if set(values) != REQUIRED_DIAG_TASKS:
        fail("canonical diagnostics representative value map is incomplete")
    metric_order = rep.get("metric_order", [])
    expected_metric_order = [
        "clean_effective_rank",
        "clean_nn_cos_dist_median",
        "transition_resolution_ratio_l2",
        "transition_resolution_ratio_cos",
        "id_probe_r2",
        "action_mean_pred_shift_norm",
    ]
    if metric_order != expected_metric_order:
        fail(
            "canonical diagnostics metric order mismatch: "
            f"expected {expected_metric_order}, got {metric_order}"
        )
    for task, task_values in values.items():
        for which in ("base", "representative"):
            if which not in task_values:
                fail(f"canonical diagnostics {task} missing {which!r} values")
            for metric in expected_metric_order:
                if metric not in task_values[which]:
                    fail(f"canonical diagnostics {task}/{which} missing metric {metric!r}")

    # Regression guard for the 2026-06-25 Table 3 audit: the compact main-text
    # diagnostic rows must stay pinned to the fixed std=0.08 per-checkpoint
    # diagnostics. Earlier drafts mixed per-task representative std values,
    # which read like an implicit selector.
    expected_representative = {
        "TwoRoom": {
            "clean_effective_rank": 37.69,
            "clean_nn_cos_dist_median": 0.0321,
            "transition_resolution_ratio_l2": 0.6621,
            "transition_resolution_ratio_cos": 0.461,
            "id_probe_r2": 0.1419,
            "action_mean_pred_shift_norm": 0.4843,
        },
        "PushT": {
            "clean_effective_rank": 78.08,
            "clean_nn_cos_dist_median": 0.2191,
            "transition_resolution_ratio_l2": 0.2789,
            "transition_resolution_ratio_cos": 0.0759,
            "id_probe_r2": 0.7647,
            "action_mean_pred_shift_norm": 0.1208,
        },
        "Reacher": {
            "clean_effective_rank": 66.2,
            "clean_nn_cos_dist_median": 0.0664,
            "transition_resolution_ratio_l2": 0.3831,
            "transition_resolution_ratio_cos": 0.144,
            "id_probe_r2": 0.1767,
            "action_mean_pred_shift_norm": 0.2619,
        },
        "Cube": {
            "clean_effective_rank": 74.97,
            "clean_nn_cos_dist_median": 0.1587,
            "transition_resolution_ratio_l2": 0.5085,
            "transition_resolution_ratio_cos": 0.2557,
            "id_probe_r2": 0.6342,
            "action_mean_pred_shift_norm": 0.2573,
        },
    }
    for task, expected in expected_representative.items():
        got = values[task]["representative"]
        for metric, want in expected.items():
            if abs(float(got[metric]) - want) > 1e-9:
                fail(
                    f"canonical diagnostics table3 {task}/representative/{metric}: "
                    f"got {got[metric]}, want {want} (fixed-0.08 Table 3 guard)"
                )


def check_pldm_diagnostics_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_diagnostics_pldm_20260522.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    predictor = data.get("predictor_metrics_by_task")
    if not isinstance(predictor, dict) or set(predictor) != REQUIRED_DIAG_TASKS:
        fail(
            "PLDM diagnostics predictor tasks mismatch: "
            f"expected {sorted(REQUIRED_DIAG_TASKS)}, got {sorted(predictor or {})}"
        )

    for task, configs in predictor.items():
        if set(configs) != EXPECTED_CONFIGS:
            fail(
                f"PLDM diagnostics {task} config mismatch: "
                f"expected {sorted(EXPECTED_CONFIGS)}, got {sorted(configs)}"
            )
        for std_key, entry in configs.items():
            for key in (
                "subdir",
                "diagnostic_max_std",
                "predictor_target_to_nn_cos_ratio_at_max_std",
                "predictor_rollout_T8_l2_at_max_std",
            ):
                if key not in entry:
                    fail(f"PLDM diagnostics {task}/{std_key} missing key {key!r}")
            for key in (
                "predictor_target_to_nn_cos_ratio_at_max_std",
                "predictor_rollout_T8_l2_at_max_std",
            ):
                if not math.isfinite(float(entry[key])):
                    fail(f"PLDM diagnostics {task}/{std_key}/{key} is not finite")


def check_pldm_full_diagnostics_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_full_diagnostics_pldm_20260523.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    by_task = data.get("diagnostics_by_task")
    if not isinstance(by_task, dict) or set(by_task) != EXPECTED_TASKS:
        fail(
            "PLDM full diagnostics task mismatch: "
            f"expected {sorted(EXPECTED_TASKS)}, got {sorted(by_task or {})}"
        )

    for task, configs in by_task.items():
        if set(configs) != EXPECTED_CONFIGS:
            fail(
                f"PLDM full diagnostics {task} config mismatch: "
                f"expected {sorted(EXPECTED_CONFIGS)}, got {sorted(configs)}"
            )
        for std_key, entry in configs.items():
            for key in ("path", "subdir", "diagnostics_summary"):
                if key not in entry:
                    fail(f"PLDM full diagnostics {task}/{std_key} missing key {key!r}")
            summary = entry["diagnostics_summary"]
            missing = EXPECTED_PLDM_FULL_DIAG_METRICS - set(summary)
            if missing:
                fail(f"PLDM full diagnostics {task}/{std_key} missing metrics: {sorted(missing)}")
            for metric in EXPECTED_PLDM_FULL_DIAG_METRICS:
                value = summary[metric]
                if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                    fail(f"PLDM full diagnostics {task}/{std_key}/{metric} is not finite")

    rep_std = data.get("representative_std_by_task", {})
    if set(rep_std) != EXPECTED_TASKS:
        fail("PLDM full diagnostics representative std map is incomplete")
    reps = data.get("representative_diagnostics", {}).get("values", {})
    if set(reps) != EXPECTED_TASKS:
        fail("PLDM full diagnostics representative values are incomplete")
    for task, entry in reps.items():
        if rep_std[task] != entry.get("representative_std"):
            fail(f"PLDM full diagnostics representative std mismatch for {task}")
        for side in ("base", "representative"):
            values = entry.get(side)
            if not isinstance(values, dict):
                fail(f"PLDM full diagnostics representative {task}/{side} missing")
            missing = EXPECTED_PLDM_FULL_DIAG_METRICS - set(values)
            if missing:
                fail(
                    f"PLDM full diagnostics representative {task}/{side} missing metrics: "
                    f"{sorted(missing)}"
                )


def check_acpc_phase0_diagnostics_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "acpc_phase0_clean_goal_seed9101.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-acpc-phase0-0.1":
        fail(f"unexpected ACPC Phase-0 schema: {meta.get('schema_version')!r}")
    if set(meta.get("methods", [])) != EXPECTED_METHODS:
        fail(f"ACPC Phase-0 methods mismatch: {meta.get('methods')}")
    if set(meta.get("tasks", [])) != EXPECTED_TASKS:
        fail(f"ACPC Phase-0 tasks mismatch: {meta.get('tasks')}")
    if set(meta.get("std_keys", [])) != EXPECTED_CONFIGS:
        fail(f"ACPC Phase-0 std keys mismatch: {meta.get('std_keys')}")
    if meta.get("dry_run") is not False:
        fail("ACPC Phase-0 artifact must be from a real run, not dry-run")
    if meta.get("corrupt_goal") is not False:
        fail("ACPC Phase-0 artifact must use clean-goal observation-noise diagnostics")

    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_METHODS) * len(EXPECTED_TASKS) * len(EXPECTED_CONFIGS):
        fail(f"ACPC Phase-0 row count mismatch: {len(rows) if isinstance(rows, list) else type(rows)}")

    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row.get("method"), row.get("task"), row.get("std_key"))
        if key in seen:
            fail(f"duplicate ACPC Phase-0 row: {key}")
        seen.add(key)
        method, task, std_key = key
        if method not in EXPECTED_METHODS or task not in EXPECTED_TASKS or std_key not in EXPECTED_CONFIGS:
            fail(f"unexpected ACPC Phase-0 row key: {key}")
        if row.get("status") != "ok":
            fail(f"ACPC Phase-0 row {key} is not ok: {row.get('status')}")
        if int(row.get("candidate_count", -1)) != 65:
            fail(f"ACPC Phase-0 row {key} unexpected candidate_count: {row.get('candidate_count')}")
        if int(row.get("rollout_horizon_actual", -1)) != 8:
            fail(f"ACPC Phase-0 row {key} unexpected rollout horizon: {row.get('rollout_horizon_actual')}")
        if int(row.get("n_sequences", -1)) != 100:
            fail(f"ACPC Phase-0 row {key} unexpected n_sequences: {row.get('n_sequences')}")
        if abs(float(row.get("noise_std", float("nan"))) - 0.08) > TOL:
            fail(f"ACPC Phase-0 row {key} unexpected noise_std: {row.get('noise_std')}")
        if row.get("corrupt_goal") is not False:
            fail(f"ACPC Phase-0 row {key} must keep the goal clean")
        missing = EXPECTED_ACPC_PHASE0_METRICS - set(row)
        if missing:
            fail(f"ACPC Phase-0 row {key} missing metrics: {sorted(missing)}")
        for metric in EXPECTED_ACPC_PHASE0_METRICS:
            value = row[metric]
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                fail(f"ACPC Phase-0 row {key}/{metric} is not finite")

    expected_seen = {
        (method, task, std_key)
        for method in EXPECTED_METHODS
        for task in EXPECTED_TASKS
        for std_key in EXPECTED_CONFIGS
    }
    if seen != expected_seen:
        fail("ACPC Phase-0 row coverage mismatch")


def check_remediation_phase1_smoke_v2() -> None:
    path = ROOT / "paper1" / "results" / "remediation_phase1_smoke_v2.json"
    data = _load_strict_json(path)
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-remediation-phase1-smoke-1.0":
        fail(f"unexpected Phase-1 smoke schema: {meta.get('schema_version')!r}")
    if meta.get("status") != "pass" or data.get("gate_status") != "pass":
        fail("Phase-1 smoke artifact does not pass Gate 1")
    checks = data.get("checks")
    if not isinstance(checks, dict) or not checks or not all(
        value is True for value in checks.values()
    ):
        fail(f"Phase-1 smoke checks are incomplete: {checks!r}")
    if meta.get("protocol_hash") is not None:
        fail("Phase-1 correctness smoke must precede protocol freezing")
    if meta.get("missing_rows") != [] or meta.get("errors") != []:
        fail("Phase-1 smoke artifact records missing rows or errors")

    expected_sources = {"acpc_0", "acpc_1", "jvp_0", "jvp_1"}
    source_paths = meta.get("source_paths", {})
    source_hashes = meta.get("source_hashes", {})
    if set(source_paths) != expected_sources or set(source_hashes) != expected_sources:
        fail("Phase-1 smoke source path/hash coverage mismatch")
    for name in sorted(expected_sources):
        source = Path(source_paths[name])
        if not source.is_absolute():
            source = ROOT / source
        if not source.is_file():
            fail(f"Phase-1 smoke source is missing: {source_paths[name]}")
        try:
            source.resolve().relative_to(ROOT.resolve())
        except ValueError:
            fail(f"Phase-1 smoke source must be preserved in-repo: {source}")
        if _sha256_file(source) != source_hashes[name]:
            fail(f"Phase-1 smoke source hash mismatch: {name}")
        source_payload = _load_strict_json(source)
        source_schema = source_payload.get("metadata", {}).get("schema_version")
        expected_schema = (
            "paper1-acpc-phase0-0.2"
            if name.startswith("acpc_")
            else "paper1-jvp-hutchinson-sensitivity-0.2"
        )
        if source_schema != expected_schema:
            fail(f"Phase-1 smoke source schema mismatch for {name}: {source_schema}")

    implementation_paths = meta.get("implementation_paths", {})
    implementation_hashes = meta.get("implementation_hashes", {})
    expected_implementations = {"canonical_metric", "acpc_runner", "jvp_runner"}
    if (
        set(implementation_paths) != expected_implementations
        or set(implementation_hashes) != expected_implementations
    ):
        fail("Phase-1 implementation path/hash coverage mismatch")
    for name in sorted(expected_implementations):
        implementation = ROOT / implementation_paths[name]
        if not implementation.is_file():
            fail(f"Phase-1 implementation is missing: {implementation_paths[name]}")
        if _sha256_file(implementation) != implementation_hashes[name]:
            # The JVP runner was deliberately corrected after Gate 1 (matched
            # weighted map and separate kappa definitions) and then rerun on
            # the complete 36-row/288-probe scope.  Preserve the original smoke
            # artifact as provenance instead of rewriting its historical hash.
            if name == "jvp_runner":
                full = _load_strict_json(
                    ROOT / "paper1/results/jvp_hutchinson_sensitivity_audit_v2.json"
                )
                if (
                    full.get("metadata", {}).get("status_counts") == {"ok": 36}
                    and len(full.get("rows", [])) == 36
                    and len(full.get("probe_rows", [])) == 288
                ):
                    continue
            fail(
                "Phase-1 implementation changed after smoke without a complete "
                f"superseding audit ({name})"
            )

    rows = data.get("benchmark_rows")
    if not isinstance(rows, list) or len(rows) != 8:
        fail(f"Phase-1 smoke expected 8 selected rows, got {type(rows)} / {len(rows) if isinstance(rows, list) else 'n/a'}")
    expected_coverage = {
        (audit, task, checkpoint)
        for audit in ("paired_rollout_radius", "jvp_hutchinson")
        for task in ("TwoRoom", "PushT")
        for checkpoint in ("base", "endpoint")
    }
    actual_coverage = {
        (row.get("audit"), row.get("task"), row.get("checkpoint_type"))
        for row in rows
    }
    if actual_coverage != expected_coverage:
        fail(f"Phase-1 smoke coverage mismatch: {sorted(actual_coverage)}")

    def require_finite(row: dict, fields: tuple[str, ...]) -> None:
        for field in fields:
            value = row.get(field)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
            ):
                fail(
                    "Phase-1 smoke row has non-finite "
                    f"{field}: {(row.get('audit'), row.get('task'), row.get('checkpoint_type'))}"
                )

    for row in rows:
        key = (row.get("audit"), row.get("task"), row.get("checkpoint_type"))
        if row.get("status") != "ok" or row.get("n_sequences") != 16:
            fail(f"Phase-1 smoke row is not a 16-anchor success: {key}")
        require_finite(
            row,
            ("model_load_time", "data_io_time", "wall_time_per_row", "peak_gpu_memory"),
        )
        if int(row["peak_gpu_memory"]) <= 0:
            fail(f"Phase-1 smoke peak GPU memory must be positive: {key}")
        if row["audit"] == "paired_rollout_radius":
            if (
                row.get("model_family") != "PLDM"
                or row.get("num_noise_draws") != 2
                or row.get("jvp_time") is not None
            ):
                fail(f"Phase-1 ACPC smoke protocol mismatch: {key}")
            require_finite(
                row,
                (
                    "atr_horizon_v2_q90",
                    "horizon_radius_v2_unnormalized_q90",
                    "stepwise_rollout_q90_compatibility_only",
                    "prediction_time",
                    "fixed_pool_time",
                ),
            )
        elif row["audit"] == "jvp_hutchinson":
            if (
                row.get("model_family") != "LeWM"
                or row.get("training_seed") != 3072
                or row.get("hutchinson_probes") != 2
                or row.get("prediction_time") is not None
                or row.get("fixed_pool_time") is not None
            ):
                fail(f"Phase-1 JVP smoke protocol mismatch: {key}")
            require_finite(
                row,
                (
                    "encoder_trace",
                    "rollout_trace",
                    "composed_trace",
                    "kappa_submultiplicative",
                    "kappa_relative_isotropic",
                    "jvp_time",
                ),
            )
        else:
            fail(f"Phase-1 smoke has unknown audit: {key}")


def check_blur_baselines_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_blur_baselines_20260523.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    baselines = data.get("baselines")
    if not isinstance(baselines, dict) or set(baselines) != EXPECTED_METHODS:
        fail(
            "blur baseline methods mismatch: "
            f"expected {sorted(EXPECTED_METHODS)}, got {sorted(baselines or {})}"
        )

    for method, by_task in baselines.items():
        if set(by_task) != EXPECTED_TASKS:
            fail(f"blur baseline {method} tasks mismatch: {sorted(by_task)}")
        for task, entry in by_task.items():
            for key in ("path", "subdir", "clean", "blur", "worst_pixels_goal_blur"):
                if key not in entry:
                    fail(f"blur baseline {method}/{task} missing key {key!r}")
            check_metric_summary(f"blur/{method}/{task}", "clean", "clean", entry["clean"])
            blur = entry["blur"]
            if set(blur) != EXPECTED_BLUR_CONDITIONS:
                fail(
                    f"blur baseline {method}/{task} condition mismatch: "
                    f"expected {sorted(EXPECTED_BLUR_CONDITIONS)}, got {sorted(blur)}"
                )
            for condition, summary in blur.items():
                check_metric_summary(f"blur/{method}/{task}", condition, condition, summary)
            worst = entry["worst_pixels_goal_blur"]
            condition = worst.get("condition")
            if condition not in blur or not condition.startswith("pixels_goal_blur_ks"):
                fail(f"blur baseline {method}/{task} has invalid worst condition {condition!r}")
            expected_worst = min(
                (blur[f"pixels_goal_blur_ks{k}"]["mean"], f"pixels_goal_blur_ks{k}")
                for k in (3, 7, 11, 15)
            )[1]
            if condition != expected_worst:
                fail(
                    f"blur baseline {method}/{task} worst mismatch: "
                    f"got {condition}, want {expected_worst}"
                )
            drop = entry["clean"]["mean"] - blur[condition]["mean"]
            if not approx_equal(drop, entry["clean_to_worst_pixels_goal_blur_drop"]):
                fail(f"blur baseline {method}/{task} drop mismatch: {drop}")


def check_acpc_basin_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "acpc_basin_diagnostics.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-acpc-basin-0.1":
        fail(f"unexpected ACPC basin schema: {meta.get('schema_version')!r}")
    if meta.get("method") != "LeWM":
        fail(f"ACPC basin method should be LeWM, got {meta.get('method')!r}")
    if meta.get("corrupt_goal") is not False:
        fail("ACPC basin metadata should mark corrupt_goal=false")

    corruptions = meta.get("corruptions")
    if not isinstance(corruptions, list) or len(corruptions) != 8:
        fail("ACPC basin metadata must list exactly 8 Gaussian-noise corruptions")
    got_magnitudes = set()
    for spec in corruptions:
        if spec.get("type") != "gaussian_noise":
            fail(f"ACPC basin contains non-noise corruption: {spec}")
        got_magnitudes.add(round(float(spec.get("magnitude")), 2))
    if got_magnitudes != EXPECTED_ACPC_BASIN_CORRUPTIONS:
        fail(
            "ACPC basin corruption grid mismatch: "
            f"got {sorted(got_magnitudes)}, want {sorted(EXPECTED_ACPC_BASIN_CORRUPTIONS)}"
        )

    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_TASKS) * len(EXPECTED_CONFIGS):
        fail("ACPC basin rows must cover 4 tasks x 9 configs")
    seen: set[tuple[str, str]] = set()
    for row in rows:
        if row.get("status") != "ok":
            fail(f"ACPC basin row is not ok: {row.get('task')}/{row.get('std_key')}")
        task = row.get("task")
        std_key = row.get("std_key")
        if task not in EXPECTED_TASKS or std_key not in EXPECTED_CONFIGS:
            fail(f"unexpected ACPC basin row key: {task}/{std_key}")
        key = (task, std_key)
        if key in seen:
            fail(f"duplicate ACPC basin row: {task}/{std_key}")
        seen.add(key)
        if row.get("method") != "LeWM":
            fail(f"ACPC basin row method should be LeWM: {task}/{std_key}")
        if row.get("corrupt_goal") is not False:
            fail(f"ACPC basin {task}/{std_key} should keep the goal clean by default")
        model_file = str(row.get("model_file", ""))
        if not model_file.endswith("epoch_10_object.ckpt"):
            fail(f"ACPC basin row does not use epoch_10 object ckpt: {model_file}")
        variants = row.get("variant_rows")
        if not isinstance(variants, list) or len(variants) != 8:
            fail(f"ACPC basin {task}/{std_key} must contain 8 variant rows")
        variant_magnitudes = set()
        for variant in variants:
            if variant.get("corruption_type") != "gaussian_noise":
                fail(f"ACPC basin {task}/{std_key} has non-noise variant: {variant}")
            variant_magnitudes.add(round(float(variant.get("magnitude")), 2))
        if variant_magnitudes != EXPECTED_ACPC_BASIN_CORRUPTIONS:
            fail(f"ACPC basin {task}/{std_key} variant grid mismatch")
        missing = REQUIRED_ACPC_BASIN_FIELDS - set(row)
        if missing:
            fail(f"ACPC basin {task}/{std_key} missing fields: {sorted(missing)}")
        for field in REQUIRED_ACPC_BASIN_FIELDS:
            value = row[field]
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                fail(f"ACPC basin {task}/{std_key}/{field} is not finite")
    if seen != {(task, std) for task in EXPECTED_TASKS for std in EXPECTED_CONFIGS}:
        fail("ACPC basin task/config coverage mismatch")


def check_acpc_basin_artifact_pointer() -> None:
    main_tex = ROOT / "paper1" / "main.tex"
    if not main_tex.exists():
        return
    tex = main_tex.read_text(encoding="utf-8")
    required = [
        "Full LeWM ACPC-basin grid",
        r"assets/paper1\_data/acpc\_basin\_diagnostics.json",
        r"\Cref{tab:acpc-basin}",
    ]
    missing = [snippet for snippet in required if snippet not in tex]
    if missing:
        fail("main.tex is missing ACPC-basin artifact pointer snippets: " + ", ".join(missing))


def check_pldm_acpc_basin_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "acpc_basin_diagnostics_pldm.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-acpc-basin-0.1":
        fail(f"unexpected PLDM ACPC basin schema: {meta.get('schema_version')!r}")
    if meta.get("method") != "PLDM" or meta.get("methods") != ["PLDM"]:
        fail(f"PLDM ACPC basin method mismatch: {meta.get('method')!r}/{meta.get('methods')!r}")
    if meta.get("base_vs_best") is not False:
        fail("PLDM ACPC basin must be the full sweep, not base-vs-best")
    if meta.get("robust_metric") != "pixels_std0.08":
        fail(f"PLDM ACPC basin robust metric mismatch: {meta.get('robust_metric')!r}")
    if meta.get("corrupt_goal") is not False:
        fail("PLDM ACPC basin metadata should mark corrupt_goal=false")
    if meta.get("dry_run") is not False:
        fail("PLDM ACPC basin artifact must be from a real run, not dry-run")

    corruptions = meta.get("corruptions")
    if not isinstance(corruptions, list) or len(corruptions) != 8:
        fail("PLDM ACPC basin metadata must list exactly 8 Gaussian-noise corruptions")
    got_magnitudes = set()
    for spec in corruptions:
        if spec.get("type") != "gaussian_noise":
            fail(f"PLDM ACPC basin contains non-noise corruption: {spec}")
        got_magnitudes.add(round(float(spec.get("magnitude")), 2))
    if got_magnitudes != EXPECTED_ACPC_BASIN_CORRUPTIONS:
        fail("PLDM ACPC basin corruption grid mismatch")

    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_TASKS) * len(EXPECTED_CONFIGS):
        fail(f"PLDM ACPC basin row count mismatch: {len(rows) if isinstance(rows, list) else type(rows)}")
    seen: set[tuple[str, str]] = set()
    for row in rows:
        task = row.get("task")
        std_key = row.get("std_key")
        key = (task, std_key)
        if task not in EXPECTED_TASKS or std_key not in EXPECTED_CONFIGS:
            fail(f"unexpected PLDM ACPC basin row key: {key}")
        if key in seen:
            fail(f"duplicate PLDM ACPC basin row: {key}")
        seen.add(key)
        if row.get("status") != "ok":
            fail(f"PLDM ACPC basin row {key} is not ok: {row.get('status')}")
        if row.get("method") != "PLDM":
            fail(f"PLDM ACPC basin row method mismatch: {key}")
        if row.get("corrupt_goal") is not False:
            fail(f"PLDM ACPC basin row should keep the goal clean: {key}")
        model_file = str(row.get("model_file", ""))
        if not model_file.endswith("epoch_10_object.ckpt"):
            fail(f"PLDM ACPC basin row does not use epoch_10 object ckpt: {model_file}")
        variants = row.get("variant_rows")
        if not isinstance(variants, list) or len(variants) != 8:
            fail(f"PLDM ACPC basin {key} must contain 8 variant rows")
        variant_magnitudes = set()
        for variant in variants:
            if variant.get("corruption_type") != "gaussian_noise":
                fail(f"PLDM ACPC basin {key} has non-noise variant: {variant}")
            variant_magnitudes.add(round(float(variant.get("magnitude")), 2))
        if variant_magnitudes != EXPECTED_ACPC_BASIN_CORRUPTIONS:
            fail(f"PLDM ACPC basin {key} variant grid mismatch")
        missing = REQUIRED_ACPC_BASIN_FIELDS - set(row)
        if missing:
            fail(f"PLDM ACPC basin {key} missing fields: {sorted(missing)}")
        for field in REQUIRED_ACPC_BASIN_FIELDS:
            value = row[field]
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                fail(f"PLDM ACPC basin {key}/{field} is not finite")
    if seen != {(task, std) for task in EXPECTED_TASKS for std in EXPECTED_CONFIGS}:
        fail("PLDM ACPC basin task/config coverage mismatch")


def check_external_baselines_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "canonical_external_baselines_20260520.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    entry = data.get("baselines", {}).get("PushT", {}).get("PLDM_clean_trained")
    if not isinstance(entry, dict):
        fail("external baseline JSON missing PushT/PLDM_clean_trained")
    if entry.get("subdir") != "pusht_pldm_baseline":
        fail(f"unexpected PLDM subdir: {entry.get('subdir')!r}")
    if (
        entry.get("citation")
        != "sobal2022jointembeddingpredictivearchitectures;sobal2025stresstesting;maes2026stableworldmodel"
    ):
        fail(f"unexpected PLDM citation key: {entry.get('citation')!r}")

    training = entry.get("training", {})
    if training.get("image_noise_std_max") != 0.0 or training.get("image_noise_noise_prob") != 0.0:
        fail("PLDM external baseline is expected to be clean-trained")

    required_eval = {"clean", "pixels_std0.08", "pixels_goal_std0.05", "pixels_goal_std0.08"}
    evaluation = entry.get("evaluation", {})
    missing = required_eval - set(evaluation)
    if missing:
        fail(f"PLDM external baseline missing eval conditions: {sorted(missing)}")
    for metric_name, summary in evaluation.items():
        check_metric_summary("PushT/PLDM_clean_trained", "external", metric_name, summary)

    clean = evaluation["clean"]["mean"]
    px08 = evaluation["pixels_std0.08"]["mean"]
    if round(clean - px08, 2) != 57.00:
        fail(f"unexpected PLDM clean-to-pixels0.08 drop: {clean - px08}")


def check_pldm_correlations_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "cross_method_corr_pldm_20260522.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    if set(data) != EXPECTED_TASKS:
        fail(f"PLDM correlation tasks mismatch: expected {sorted(EXPECTED_TASKS)}, got {sorted(data)}")

    expected_push = {
        ("within_pldm", "partial_metric_drop_on_std"): -0.05,
        ("joint", "partial_metric_drop_on_std_method"): 0.22,
    }
    for task, block in data.items():
        rows = block.get("rows", {})
        if len(rows.get("pldm", [])) != 9 or len(rows.get("lewm", [])) != 9:
            fail(f"PLDM correlation {task} expected 9 LeWM rows and 9 PLDM rows")
        within = block.get("within_pldm", {}).get("frag", {})
        joint = block.get("joint", {}).get("frag", {})
        if within.get("n") != 9:
            fail(f"PLDM correlation {task} within-PLDM n mismatch: {within.get('n')}")
        if joint.get("n") != 18:
            fail(f"PLDM correlation {task} joint n mismatch: {joint.get('n')}")
        for key in (
            "partial_metric_clean_on_std",
            "partial_metric_px08_on_std",
            "partial_metric_drop_on_std",
        ):
            if key not in within or not math.isfinite(float(within[key])):
                fail(f"PLDM correlation {task}/within_pldm/frag missing finite {key}")
        if (
            "partial_metric_drop_on_std_method" not in joint
            or not math.isfinite(float(joint["partial_metric_drop_on_std_method"]))
        ):
            fail(f"PLDM correlation {task}/joint/frag missing finite partial drop")

    for (section, key), want in expected_push.items():
        got = round2(data["PushT"][section]["frag"][key])
        if got != want:
            fail(f"PLDM PushT correlation mismatch for {section}/{key}: got {got}, want {want}")


def _check_bootstrap_cell(
    data: dict,
    task: str,
    scope: str,
    metric: str,
    key: str,
    point: float,
    ci: tuple[float, float],
) -> None:
    cell = data["by_task"][task][scope][metric][key]
    got_point = round2(cell.get("point"))
    if got_point != point:
        fail(
            f"bootstrap point mismatch for {task}/{scope}/{metric}/{key}: "
            f"got {got_point}, want {point}"
        )
    got_ci = cell.get("ci")
    if not isinstance(got_ci, list) or len(got_ci) != 2:
        fail(f"bootstrap CI missing for {task}/{scope}/{metric}/{key}")
    if round2(got_ci[0]) != ci[0] or round2(got_ci[1]) != ci[1]:
        fail(
            f"bootstrap CI mismatch for {task}/{scope}/{metric}/{key}: "
            f"got {[round2(got_ci[0]), round2(got_ci[1])]}, want {list(ci)}"
        )


def check_partial_corr_bootstrap_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "partial_corr_bootstrap_20260523.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    meta = data.get("metadata", {})
    if meta.get("n_bootstrap") != 1000 or meta.get("seed") != 42:
        fail(f"unexpected bootstrap metadata: {meta}")
    if meta.get("ci_low_pct") != 2.5 or meta.get("ci_high_pct") != 97.5:
        fail(f"unexpected bootstrap CI percentiles: {meta}")

    by_task = data.get("by_task")
    if not isinstance(by_task, dict) or set(by_task) != EXPECTED_TASKS:
        fail(
            "bootstrap tasks mismatch: "
            f"expected {sorted(EXPECTED_TASKS)}, got {sorted(by_task or {})}"
        )
    for task, block in by_task.items():
        if set(block) != EXPECTED_BOOTSTRAP_SCOPES:
            fail(f"bootstrap {task} scopes mismatch: {sorted(block)}")
        for scope, scope_block in block.items():
            expected_n = 18 if scope == "joint" else 9
            if scope_block.get("n") != expected_n:
                fail(f"bootstrap {task}/{scope} n mismatch: {scope_block.get('n')}")
            if not EXPECTED_BOOTSTRAP_METRICS.issubset(scope_block):
                fail(f"bootstrap {task}/{scope} missing metrics")
            for metric in EXPECTED_BOOTSTRAP_METRICS:
                cells = scope_block[metric]
                if not isinstance(cells, dict):
                    fail(f"bootstrap {task}/{scope}/{metric} is not a dict")
                for cell_name, cell in cells.items():
                    if "point" not in cell or "n_valid" not in cell or "ci" not in cell:
                        fail(f"bootstrap {task}/{scope}/{metric}/{cell_name} malformed")
                    if cell["point"] is not None and not math.isfinite(float(cell["point"])):
                        fail(f"bootstrap {task}/{scope}/{metric}/{cell_name} point not finite")
                    if not isinstance(cell["n_valid"], int) or cell["n_valid"] < 0:
                        fail(f"bootstrap {task}/{scope}/{metric}/{cell_name} invalid n_valid")

    # Values quoted in main.tex contributions / Table 7 / Appendix F. These are rounded
    # checks, not a substitute for rerunning the bootstrap.
    _check_bootstrap_cell(
        data, "PushT", "within_lewm", "frag", "partial_metric_clean_on_std",
        -0.59, (-0.97, -0.10),
    )
    _check_bootstrap_cell(
        data, "PushT", "within_lewm", "frag", "partial_metric_px08_on_std",
        -0.53, (-0.84, 0.00),
    )
    _check_bootstrap_cell(
        data, "PushT", "within_lewm", "frag", "partial_metric_drop_on_std",
        0.19, (-0.00, 0.70),
    )
    _check_bootstrap_cell(
        data, "PushT", "within_pldm", "frag", "partial_metric_drop_on_std",
        -0.05, (-0.92, 0.61),
    )
    _check_bootstrap_cell(
        data, "PushT", "joint", "frag", "partial_metric_drop_on_std_method",
        0.22, (-0.59, 0.61),
    )
    _check_bootstrap_cell(
        data, "Reacher", "within_lewm", "drift", "partial_metric_drop_on_std",
        0.37, (-0.35, 0.99),
    )


def check_three_seed_gaussian_sweep_summary_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "three_seed_gaussian_sweep_summary_20260706.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-three-seed-gaussian-sweep-summary-20260706-v1":
        fail(f"three-seed Gaussian sweep schema changed: {meta.get('schema_version')!r}")
    if meta.get("tasks") != ["TwoRoom", "PushT", "Reacher", "Cube"]:
        fail(f"three-seed Gaussian sweep task order changed: {meta.get('tasks')}")
    if meta.get("training_seeds") != [3072, 3073, 3074]:
        fail(f"three-seed Gaussian sweep seeds changed: {meta.get('training_seeds')}")
    if set(meta.get("sweep_stdmax", [])) != EXPECTED_CONFIGS:
        fail(f"three-seed Gaussian sweep std grid changed: {meta.get('sweep_stdmax')}")
    if set(meta.get("metric_keys", {})) != THREE_SEED_SWEEP_METRICS:
        fail(f"three-seed Gaussian sweep metric keys changed: {meta.get('metric_keys')}")

    summary_rows = data.get("summary_rows", [])
    per_seed_rows = data.get("per_seed_rows", [])
    if len(summary_rows) != len(EXPECTED_TASKS) * len(EXPECTED_CONFIGS):
        fail(f"three-seed Gaussian sweep expected 36 summary rows, got {len(summary_rows)}")
    if len(per_seed_rows) != len(EXPECTED_TASKS) * len(EXPECTED_CONFIGS) * 3:
        fail(f"three-seed Gaussian sweep expected 108 per-seed rows, got {len(per_seed_rows)}")

    per_seed = {}
    for row in per_seed_rows:
        key = (row.get("task"), str(row.get("stdmax")), int(row.get("training_seed")))
        if key in per_seed:
            fail(f"duplicate three-seed Gaussian per-seed row: {key}")
        if key[0] not in EXPECTED_TASKS or key[1] not in EXPECTED_CONFIGS or key[2] not in (3072, 3073, 3074):
            fail(f"unexpected three-seed Gaussian per-seed key: {key}")
        metrics = row.get("metrics", {})
        if set(metrics) != THREE_SEED_SWEEP_METRICS:
            fail(f"three-seed Gaussian per-seed metrics changed for {key}: {sorted(metrics)}")
        for metric, cell in metrics.items():
            values = cell.get("eval_seed_values", [])
            if not isinstance(values, list) or len(values) != 3:
                fail(f"three-seed Gaussian {key}/{metric} must contain three eval-seed values")
            if not all(isinstance(v, (int, float)) for v in values):
                fail(f"three-seed Gaussian {key}/{metric} has non-numeric eval-seed values")
            mean = statistics.fmean(values)
            if not math.isclose(float(cell.get("mean_over_eval_seeds")), mean, rel_tol=0.0, abs_tol=1e-6):
                fail(f"three-seed Gaussian {key}/{metric} eval-seed mean mismatch")
        per_seed[key] = row

    summary = {}
    for row in summary_rows:
        key = (row.get("task"), str(row.get("stdmax")))
        if key in summary:
            fail(f"duplicate three-seed Gaussian summary row: {key}")
        if key[0] not in EXPECTED_TASKS or key[1] not in EXPECTED_CONFIGS:
            fail(f"unexpected three-seed Gaussian summary key: {key}")
        if row.get("training_seeds") != [3072, 3073, 3074] or row.get("n_training_seeds") != 3:
            fail(f"three-seed Gaussian summary row must use seeds 3072/3073/3074: {key}")
        metrics = row.get("metrics", {})
        if set(metrics) != THREE_SEED_SWEEP_METRICS:
            fail(f"three-seed Gaussian summary metrics changed for {key}: {sorted(metrics)}")
        for metric, cell in metrics.items():
            values = [
                float(per_seed[(key[0], key[1], seed)]["metrics"][metric]["mean_over_eval_seeds"])
                for seed in (3072, 3073, 3074)
            ]
            if [round(float(v), 6) for v in cell.get("per_training_seed_means", [])] != [round(v, 6) for v in values]:
                fail(f"three-seed Gaussian {key}/{metric} per-training-seed means mismatch")
            if not math.isclose(float(cell.get("mean")), statistics.fmean(values), rel_tol=0.0, abs_tol=1e-6):
                fail(f"three-seed Gaussian {key}/{metric} mean mismatch")
            if not math.isclose(float(cell.get("pstdev")), statistics.pstdev(values), rel_tol=0.0, abs_tol=1e-6):
                fail(f"three-seed Gaussian {key}/{metric} pstdev mismatch")
        summary[key] = row

    expected_obs08 = {
        "TwoRoom": 97.11,
        "PushT": 85.78,
        "Reacher": 81.56,
        "Cube": 62.56,
    }
    for task, want in expected_obs08.items():
        got = round2(float(summary[(task, "0.08")]["metrics"]["obs_sigma_0.08"]["mean"]))
        if got != want:
            fail(f"three-seed Gaussian std=0.08 obs endpoint changed for {task}: {got} != {want}")


def check_training_seed_gaussian_lockbox_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "training_seed_gaussian_lockbox.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("task_summary_rows", [])
    by_task = {row.get("task"): row for row in rows}
    expected = {
        "TwoRoom": (97.10888888888888, 28.333333333333332),
        "PushT": (85.77666666666666, 78.55555555555556),
        "Reacher": (81.55333333333333, 63.33555555555555),
        "Cube": (62.55666666666667, 19.44666666666667),
    }
    if set(by_task) != set(expected):
        fail(f"training-seed lockbox tasks mismatch: got {sorted(by_task)}")
    for task, (want_std08, want_gain) in expected.items():
        row = by_task[task]
        if row.get("training_seeds") != [3072, 3073, 3074]:
            fail(f"{task} training-seed lockbox must use seeds 3072/3073/3074")
        got_std08 = float(row["std_0p08_obs_0p08_mean"])
        got_gain = float(row["std_0p08_gain_over_baseline_mean"])
        if not approx_equal(got_std08, want_std08) or not approx_equal(got_gain, want_gain):
            fail(
                f"{task} training-seed lockbox mismatch: "
                f"got std08={got_std08}, gain={got_gain}; "
                f"want std08={want_std08}, gain={want_gain}"
            )


def check_prospective_validation_summary_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "prospective_validation_summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    required_sources = {
        "assets/paper1_data/unseen_origin_vs_std008_strongest_s3072.json",
        "assets/paper1_data/unseen_origin_vs_std008_strongest_s3073.json",
        "assets/paper1_data/unseen_origin_vs_std008_strongest_s3074.json",
        "assets/paper1_data/unseen_phase0_acpc_subset.json",
        "assets/paper1_data/unseen_phase0_acpc_fullstress.json",
    }
    sources = set(data.get("metadata", {}).get("source_artifacts", []))
    if not required_sources.issubset(sources):
        fail("prospective validation summary must cite all three-seed unseen score artifacts")
    for source in sorted(s for s in required_sources if "origin_vs" in s):
        source_data = json.loads((ROOT / source).read_text(encoding="utf-8"))
        status = source_data.get("metadata", {}).get("status", "")
        if "audited score artifact" not in status:
            fail(f"{source} must be marked as an audited unseen score artifact")

    score_summary = data.get("three_seed_unseen_score_summary", {})
    selected_policy = {
        "TwoRoom": "gaussian_blur",
        "PushT": "resize",
        "Reacher": "gaussian_blur",
        "Cube": "resize",
    }
    if score_summary.get("selected_stress_policy") != selected_policy:
        fail("three-seed unseen score summary selected-stress policy changed")

    coverage = score_summary.get("coverage", {})
    expected_coverage = {
        f"{task}:{family}": [3072, 3073, 3074]
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for family in ("gaussian_blur", "resize")
    }
    if coverage != expected_coverage:
        fail(f"three-seed unseen score coverage mismatch: {coverage}")

    selected = {
        (row.get("task"), row.get("family")): row
        for row in score_summary.get("selected_stress_rows", [])
    }
    expected_selected = {
        ("TwoRoom", "gaussian_blur"): (47.67, 90.78, 43.11, 40.89),
        ("PushT", "resize"): (63.44, 66.33, 2.89, -3.78),
        ("Reacher", "gaussian_blur"): (22.00, 71.22, 49.22, 30.22),
        ("Cube", "resize"): (57.00, 56.11, -0.89, 2.78),
    }
    if set(selected) != set(expected_selected):
        fail(f"three-seed unseen selected rows mismatch: {sorted(selected)}")
    for row_key, expected_values in expected_selected.items():
        row = selected[row_key]
        if row.get("training_seeds") != [3072, 3073, 3074] or row.get("n_training_seeds") != 3:
            fail(f"{row_key} unseen score row must use training seeds 3072/3073/3074")
        got_values = (
            round2(float(row["baseline_stress_success_mean"])),
            round2(float(row["std008_stress_success_mean"])),
            round2(float(row["stress_success_delta_mean"])),
            round2(float(row["drop_improvement_mean"])),
        )
        if got_values != expected_values:
            fail(f"{row_key} three-seed unseen score mismatch: got {got_values}, want {expected_values}")

    heldout = data.get("heldout_unseen_validation", {})
    if heldout.get("n_rows") != 12:
        fail("prospective validation summary must contain the 12-row three-seed unseen diagnostic slice")
    rows = {row.get("metric"): row for row in heldout.get("metric_rows", [])}
    composite = rows.get("Composite signed-rank rule")
    if composite is None:
        fail("prospective validation summary missing composite signed-rank row")
    checks = {
        "spearman_vs_stress_success_delta": 0.94,
        "pearson_vs_stress_success_delta": 0.96,
        "spearman_vs_drop_improvement": 0.83,
        "pearson_vs_drop_improvement": 0.86,
    }
    for key, want in checks.items():
        got = round2(float(composite[key]))
        if got != want:
            fail(f"prospective validation composite {key} mismatch: got {got}, want {want}")
    topk = heldout.get("topk_summary", {})
    if topk.get("stress_success_delta_topk_hit_count") != 4 or topk.get("drop_improvement_topk_hit_count") != 2:
        fail("prospective validation top-4 agreement must remain 4/4 for stress delta and 2/4 for drop improvement on the three-seed unseen slice")
    fullstress = data.get("fullstress_unseen_validation", {})
    if fullstress.get("n_rows") != 24:
        fail("prospective validation summary must contain the 24-row full blur/resize unseen diagnostic slice")
    full_rows = {row.get("metric"): row for row in fullstress.get("metric_rows", [])}
    full_composite = full_rows.get("Composite signed-rank rule")
    if full_composite is None:
        fail("prospective validation summary missing fullstress composite signed-rank row")
    full_checks = {
        "spearman_vs_stress_success_delta": 0.94,
        "pearson_vs_stress_success_delta": 0.94,
        "spearman_vs_drop_improvement": 0.82,
        "pearson_vs_drop_improvement": 0.84,
    }
    for key, want in full_checks.items():
        got = round2(float(full_composite[key]))
        if got != want:
            fail(f"fullstress validation composite {key} mismatch: got {got}, want {want}")
    full_topk = fullstress.get("topk_summary", {})
    if full_topk.get("stress_success_delta_topk_hit_count") != 4 or full_topk.get("drop_improvement_topk_hit_count") != 2:
        fail("fullstress validation top-4 agreement must remain 4/4 for stress delta and 2/4 for drop improvement")
    diag = data.get("three_seed_full_grid_diagnostic_validation", {})
    if diag.get("n_task_seed_blocks") != 12 or diag.get("within_5pp_hits") != 10:
        fail("prospective validation summary must include completed three-seed full-grid diagnostic validation")
    split_rows = {row.get("split"): row for row in data.get("three_seed_diagnostic_split_summaries", [])}
    heldout = split_rows.get("heldout_training_seeds_3073_3074")
    if heldout is None:
        fail("prospective validation summary missing held-out training-seed diagnostic split")
    if (heldout.get("n_task_seed_blocks"), heldout.get("n_checkpoint_candidates"), heldout.get("within_5pp_hits")) != (8, 64, 7):
        fail(f"held-out training-seed diagnostic split changed: {heldout}")
    if round2(float(heldout.get("mean_selected_regret_to_best_pp"))) != 2.21:
        fail("held-out diagnostic split mean regret changed")
    semantic_rows = data.get("semantic_margin_passrate", [])
    if len(semantic_rows) != 8:
        fail("prospective validation summary must include completed task-state proxy margin pass-rate rows")
    semantic_cov = data.get("semantic_margin_coverage", {})
    expected_semantic_cov = {
        f"{task}:{std}": [3072, 3073, 3074]
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for std in ("0.0", "0.08")
    }
    if semantic_cov != expected_semantic_cov:
        fail(f"prospective validation task-state proxy margin coverage mismatch: {semantic_cov}")





def check_prospective_atr_smpr_validation() -> None:
    smpr_path = ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_lewm_full_sweep_20260708.json"
    smpr = json.loads(smpr_path.read_text(encoding="utf-8"))
    rows = [row for row in smpr.get("rows", []) if row.get("status") == "ok"]
    if len(rows) != 108:
        fail(f"full-sweep SMPR must contain 108 ok rows, got {len(rows)}")
    coverage = {(row["task"], int(row["training_seed"]), str(row["std_key"])) for row in rows}
    expected = {(task, seed, std) for task in EXPECTED_TASKS for seed in (3072, 3073, 3074) for std in EXPECTED_CONFIGS}
    if coverage != expected:
        fail("full-sweep SMPR coverage mismatch")
    if len(smpr.get("summary_rows", [])) != 36:
        fail("full-sweep SMPR summary must cover 4 tasks x 9 std keys")

    main_text = (ROOT / "paper1" / "main.tex").read_text(encoding="utf-8")
    forbidden_main = (
        "per-task ATR+SMPR precision",
        "mean interval IoU",
        "F1 0.96",
        "separate ATR/SMPR threshold audit",
    )
    for snippet in forbidden_main:
        if snippet in main_text:
            fail(f"paper-facing prospective validation must not contain old threshold-classifier wording: {snippet}")

    out_dir = ROOT / "paper1" / "results" / "diagnostic_region"
    region = list(csv.DictReader((out_dir / "diagnostic_region_summary.csv").open(encoding="utf-8")))
    direction = list(csv.DictReader((out_dir / "direction_consistency_summary.csv").open(encoding="utf-8")))
    separation = list(csv.DictReader((out_dir / "robust_fragile_separation.csv").open(encoding="utf-8")))

    def row_for(table: list[dict[str, str]], **criteria: str) -> dict[str, str]:
        row = next((r for r in table if all(r.get(k) == v for k, v in criteria.items())), None)
        if row is None:
            fail(f"diagnostic-region table missing row: {criteria}")
        return row

    expected_counts = {
        ("heldout", "fragile"): 8,
        ("heldout", "transition"): 13,
        ("heldout", "robust"): 51,
        ("all", "fragile"): 13,
        ("all", "transition"): 19,
        ("all", "robust"): 76,
    }
    for (split, regime), want in expected_counts.items():
        got = int(row_for(region, split=split, regime=regime)["n"])
        if got != want:
            fail(f"diagnostic-region {split}/{regime} count mismatch: got {got}, want {want}")

    heldout_fragile = row_for(region, split="heldout", regime="fragile")
    heldout_robust = row_for(region, split="heldout", regime="robust")
    checks = {
        "heldout fragile median normalized ATR": (float(heldout_fragile["atr_rel_q50"]), 1.0),
        "heldout fragile median SMPR": (float(heldout_fragile["smpr_q50"]), 0.4349999874830246),
        "heldout robust median normalized ATR": (float(heldout_robust["atr_rel_q50"]), 0.08666369301340819),
        "heldout robust median SMPR": (float(heldout_robust["smpr_q50"]), 0.9999999403953552),
    }
    for label, (got, want) in checks.items():
        if abs(got - want) > 1e-9:
            fail(f"{label} mismatch: got {got}, want {want}")

    heldout_direction = row_for(direction, split="heldout")
    all_direction = row_for(direction, split="all")
    if (
        int(heldout_direction["eligible_blocks"]),
        int(heldout_direction["atr_direction_ok"]),
        int(heldout_direction["smpr_direction_ok"]),
        int(heldout_direction["joint_direction_ok"]),
    ) != (8, 8, 8, 8):
        fail(f"held-out diagnostic direction consistency mismatch: {heldout_direction}")
    if (
        int(all_direction["eligible_blocks"]),
        int(all_direction["atr_direction_ok"]),
        int(all_direction["smpr_direction_ok"]),
        int(all_direction["joint_direction_ok"]),
    ) != (12, 12, 12, 12):
        fail(f"all-seed diagnostic direction consistency mismatch: {all_direction}")

    heldout_sep = row_for(separation, split="heldout")
    if int(heldout_sep["robust_atr_q75_below_fragile_q25"]) != 1:
        fail("held-out robust ATR IQR must stay below fragile ATR IQR")
    if int(heldout_sep["robust_smpr_q25_above_fragile_q75"]) != 1:
        fail("held-out robust SMPR IQR must stay above fragile SMPR IQR")
    if float(heldout_sep["atr_rel_median_gap"]) <= 0.9 or float(heldout_sep["smpr_median_gap"]) <= 0.5:
        fail(f"held-out recovered-vs-fragile separation is weaker than expected: {heldout_sep}")

def check_selector_baseline_audit_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "selector_baseline_audit_20260704.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-selector-baseline-audit-20260704-v1":
        fail(f"selector-baseline audit schema changed: {meta.get('schema_version')!r}")
    if meta.get("score") != "pixels_std0.08_success":
        fail("selector-baseline audit must target pixels_std0.08_success")
    rows = data.get("selection_rows", [])
    if len(rows) != 96:
        fail(f"selector-baseline audit expected 96 selection rows, got {len(rows)}")
    selectors = {
        "aggregate_rank_acpc_pcc_cra_maf",
        "fixed_std_0.08",
        "best_acpc_only",
        "best_pcc_only",
        "best_cra_only",
        "best_maf_only",
        "random_nonzero_std",
        "oracle_best",
    }
    keys = {(row.get("task"), int(row.get("training_seed")), row.get("selector")) for row in rows}
    expected_keys = {
        (task, seed, selector)
        for task in EXPECTED_TASKS
        for seed in (3072, 3073, 3074)
        for selector in selectors
    }
    if keys != expected_keys:
        fail("selector-baseline audit row coverage mismatch")

    splits = {entry.get("split"): entry for entry in data.get("split_summaries", [])}
    expected_splits = {
        "all_three_training_seeds",
        "development_seed_3072",
        "heldout_training_seeds_3073_3074",
    }
    if set(splits) != expected_splits:
        fail(f"selector-baseline audit splits changed: {sorted(splits)}")

    expected = {
        "all_three_training_seeds": {
            "aggregate_rank_acpc_pcc_cra_maf": (12, 10, 3, 2.25),
            "fixed_std_0.08": (12, 10, 4, 2.14),
            "best_maf_only": (12, 10, 5, 1.89),
            "random_nonzero_std": (12, None, None, 7.02),
            "oracle_best": (12, 12, 12, 0.00),
        },
        "heldout_training_seeds_3073_3074": {
            "aggregate_rank_acpc_pcc_cra_maf": (8, 7, 1, 2.21),
            "fixed_std_0.08": (8, 7, 2, 2.08),
            "best_maf_only": (8, 7, 2, 1.62),
            "random_nonzero_std": (8, None, None, 7.23),
            "oracle_best": (8, 8, 8, 0.00),
        },
    }
    for split, split_expected in expected.items():
        row_map = {row.get("selector"): row for row in splits[split].get("rows", [])}
        for selector, (want_n, want_within, want_exact, want_regret) in split_expected.items():
            row = row_map.get(selector)
            if row is None:
                fail(f"selector-baseline audit missing {split}/{selector}")
            if int(row.get("n_task_seed_blocks")) != want_n:
                fail(f"selector-baseline audit {split}/{selector} n changed")
            if want_within is None:
                if row.get("within_5pp_hits") is not None:
                    fail(f"selector-baseline audit {split}/{selector} within should be None")
            elif int(row.get("within_5pp_hits")) != want_within:
                fail(f"selector-baseline audit {split}/{selector} within changed")
            if want_exact is None:
                if row.get("exact_best_hits") is not None:
                    fail(f"selector-baseline audit {split}/{selector} exact should be None")
            elif int(row.get("exact_best_hits")) != want_exact:
                fail(f"selector-baseline audit {split}/{selector} exact changed")
            got_regret = round2(float(row.get("mean_regret_to_best_pp")))
            if got_regret != want_regret:
                fail(
                    f"selector-baseline audit {split}/{selector} regret changed: "
                    f"got {got_regret}, want {want_regret}"
                )


def check_selector_plateau_audit_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "selector_plateau_audit_20260704.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-plateau-membership-audit-20260704-v2":
        fail(f"selector plateau audit schema changed: {meta.get('schema_version')!r}")
    if round2(float(meta.get("tolerance_pp"))) != 5.00:
        fail("selector plateau audit tolerance must remain 5pp")
    if int(meta.get("screen_size_per_block")) != 4:
        fail("selector plateau audit must screen top half of nonzero candidates")
    interp = meta.get("interpretation", "")
    if "Plateau-membership screen" not in interp or "candidate label" not in interp:
        fail("selector plateau audit must state plateau-membership/candidate-label framing")
    if "point-optimal selector target" not in interp:
        fail("selector plateau audit must reject point-optimal selector framing")

    rows = data.get("membership_summaries", [])
    if len(rows) != 7:
        fail(f"selector plateau audit expected 7 membership summaries, got {len(rows)}")
    row_map = {row.get("rule"): row for row in rows}
    expected = {
        "Aggregate ACPC/PCC/CRA/MAF": (12, 48, 68, 42, 6, 26, 22, 0.875, 0.618),
        "ACPC only": (12, 48, 68, 42, 6, 26, 22, 0.875, 0.618),
        "PCC only": (12, 48, 68, 42, 6, 26, 22, 0.875, 0.618),
        "CRA only": (12, 48, 68, 42, 6, 26, 22, 0.875, 0.618),
        "MAF only": (12, 48, 68, 44, 4, 24, 24, 0.917, 0.647),
        "High-std top-half reference": (12, 48, 68, 42, 6, 26, 22, 0.875, 0.618),
    }
    random_name = "Random top-half reference (exact expectation)"
    if set(row_map) != set(expected) | {random_name}:
        fail(f"selector plateau audit membership rows changed: {sorted(row_map)}")
    for rule, want in expected.items():
        row = row_map[rule]
        got = (
            int(row.get("plateau_presence_hits")),
            int(row.get("screened_rows")),
            int(row.get("true_plateau_rows")),
            int(row.get("true_positive_rows")),
            int(row.get("false_positive_rows")),
            int(row.get("false_negative_rows")),
            int(row.get("true_negative_rows")),
            round(float(row.get("screen_precision")), 3),
            round(float(row.get("plateau_recall")), 3),
        )
        if got != want:
            fail(f"selector plateau audit {rule} changed: got {got}, want {want}")
    random_row = row_map[random_name]
    got_random = (
        round2(float(random_row.get("plateau_presence_hits_expected"))),
        int(random_row.get("screened_rows")),
        int(random_row.get("true_plateau_rows")),
        round2(float(random_row.get("true_positive_rows_expected"))),
        round2(float(random_row.get("false_positive_rows_expected"))),
        round2(float(random_row.get("false_negative_rows_expected"))),
        round2(float(random_row.get("true_negative_rows_expected"))),
        round(float(random_row.get("screen_precision_expected")), 3),
        round(float(random_row.get("plateau_recall_expected")), 3),
    )
    want_random = (11.96, 48, 68, 34.00, 14.00, 34.00, 14.00, 0.708, 0.500)
    if got_random != want_random:
        fail(f"selector plateau audit random reference changed: got {got_random}, want {want_random}")

def check_residual_diagnostic_audit_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "residual_diagnostic_audit_20260704.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-residual-diagnostic-audit-0.1":
        fail(f"residual diagnostic audit schema changed: {meta.get('schema_version')!r}")
    controls = meta.get("controls", "")
    if "std_max" not in controls or "task fixed effects" not in controls or "training-seed" not in controls:
        fail("residual diagnostic audit controls must include std_max, task, and training seed")
    rows = data.get("metric_rows", [])
    if len(rows) != 8:
        fail(f"residual diagnostic audit expected 8 metric rows, got {len(rows)}")
    expected = {
        ("ACPC-H/trans.", "obs0.08 success"): (0.41, 0.07, -0.22, 0.30),
        ("ACPC-H/trans.", "reduced drop"): (0.62, 0.19, 0.06, 0.36),
        ("PCC", "obs0.08 success"): (0.38, 0.09, -0.16, 0.33),
        ("PCC", "reduced drop"): (0.60, 0.20, 0.06, 0.37),
        ("CRA", "obs0.08 success"): (0.15, 0.23, -0.07, 0.47),
        ("CRA", "reduced drop"): (0.54, 0.29, 0.14, 0.45),
        ("MAF", "obs0.08 success"): (-0.02, 0.30, 0.07, 0.48),
        ("MAF", "reduced drop"): (0.45, 0.23, 0.11, 0.34),
    }
    got_keys = {(row.get("metric"), row.get("outcome")) for row in rows}
    if got_keys != set(expected):
        fail(f"residual diagnostic audit row keys changed: {sorted(got_keys)}")
    for row in rows:
        key = (row.get("metric"), row.get("outcome"))
        if int(row.get("n_rows")) != 96:
            fail(f"residual diagnostic audit {key} n_rows changed")
        if int(row.get("n_task_seed_blocks")) != 12:
            fail(f"residual diagnostic audit {key} block count changed")
        if int(row.get("n_bootstrap_valid")) != 2000:
            fail(f"residual diagnostic audit {key} bootstrap count changed")
        want_ord, want_partial, want_lo, want_hi = expected[key]
        got_ord = round2(float(row.get("ordinary_spearman_signed")))
        got_partial = round2(float(row.get("partial_spearman_signed_controlling_std_task_seed")))
        got_lo, got_hi = [round2(float(x)) for x in row.get("block_bootstrap_ci95", [])]
        got = (got_ord, got_partial, got_lo, got_hi)
        want = (want_ord, want_partial, want_lo, want_hi)
        if got != want:
            fail(f"residual diagnostic audit {key} changed: got {got}, want {want}")


def check_selector_incremental_audit_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "selector_incremental_audit_20260704.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-selector-incremental-audit-0.1":
        fail(f"selector incremental audit schema changed: {meta.get('schema_version')!r}")
    controls = set(meta.get("controls", []))
    required_controls = {"std_max", "std_max^2", "task fixed effects", "training-seed fixed effects"}
    if not required_controls.issubset(controls):
        fail(f"selector incremental audit controls changed: {controls}")
    rows = data.get("compact_rows", [])
    if len(rows) != 6:
        fail(f"selector incremental audit expected 6 compact rows, got {len(rows)}")
    row_map = {row.get("metric"): row for row in rows}
    expected = {
        "Aggregate ACPC/PCC/CRA/MAF": (0.16, 0.03, 0.01, 0.07, 0.11),
        "ACPC-H/trans.": (0.12, 0.01, 0.01, 0.16, -0.08),
        "PCC": (0.13, 0.02, 0.01, 0.12, -0.04),
        "CRA": (0.23, 0.05, 0.03, 0.005, 0.10),
        "MAF": (0.15, 0.02, 0.01, 0.12, 0.15),
        "Elite overlap": (0.13, 0.02, 0.01, 0.18, -0.01),
    }
    if set(row_map) != set(expected):
        fail(f"selector incremental audit metrics changed: {sorted(row_map)}")
    for metric, want in expected.items():
        row = row_map[metric]
        got = (
            round2(float(row["reduced_drop_partial_r"])),
            round2(float(row["reduced_drop_partial_r2"])),
            round2(float(row["reduced_drop_incremental_r2"])),
            round(float(row["reduced_drop_block_permutation_p"]), 3) if metric == "CRA" else round2(float(row["reduced_drop_block_permutation_p"])),
            round2(float(row["obs008_success_partial_r"])),
        )
        want_tuple = (want[0], want[1], want[2], want[3], want[4])
        if got != want_tuple:
            fail(f"selector incremental audit {metric} changed: got {got}, want {want_tuple}")
    metric_rows = data.get("metric_rows", [])
    if len(metric_rows) != 12:
        fail(f"selector incremental audit expected 12 full metric rows, got {len(metric_rows)}")
    if any(int(row.get("n", 0)) != 96 for row in metric_rows):
        fail("selector incremental audit full rows must use 96 nonzero checkpoint rows")


def check_semantic_task_grounded_margin_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "semantic_task_grounded_margin_lewm_three_seed.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("pair_rule") != "task_grounded_near_boundary":
        fail("task-grounded semantic margin artifact must use task_grounded_near_boundary")
    if round2(float(meta.get("local_quantile"))) != 0.35:
        fail("task-grounded semantic margin local quantile changed")
    rows = data.get("rows", [])
    if len(rows) != 24 or any(row.get("status") != "ok" for row in rows):
        fail("task-grounded semantic margin artifact must contain 24 ok rows")
    coverage = data.get("coverage", {})
    expected_coverage = {
        f"{task}:{std}": [3072, 3073, 3074]
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for std in ("0.0", "0.08")
    }
    if coverage != expected_coverage:
        fail(f"task-grounded semantic margin coverage mismatch: {coverage}")
    expected_pair_counts = {"TwoRoom": 61, "PushT": 98, "Reacher": 100, "Cube": 100}
    for row in rows:
        task = row.get("task")
        if int(row.get("semantic_pair_count")) != expected_pair_counts[task]:
            fail(f"task-grounded semantic pair count changed for {task}: {row.get('semantic_pair_count')}")
        if "task-grounded" not in row.get("semantic_factor", ""):
            fail(f"task-grounded semantic factor missing for {task}")
    summary = {(row["task"], row["std_key"]): row for row in data.get("summary_rows", [])}
    expected_pass = {
        ("TwoRoom", "0.0"): 0.34,
        ("TwoRoom", "0.08"): 0.99,
        ("PushT", "0.0"): 0.44,
        ("PushT", "0.08"): 1.00,
        ("Reacher", "0.0"): 0.73,
        ("Reacher", "0.08"): 1.00,
        ("Cube", "0.0"): 0.45,
        ("Cube", "0.08"): 1.00,
    }
    if set(summary) != set(expected_pass):
        fail(f"task-grounded semantic summary rows mismatch: {sorted(summary)}")
    for key, want in expected_pass.items():
        got = round2(float(summary[key]["semantic_margin_pass_rate_mean"]))
        if got != want:
            fail(f"task-grounded semantic pass-rate mismatch for {key}: got {got}, want {want}")
    if round2(float(summary[("TwoRoom", "0.08")]["semantic_margin_median_mean"])) != 15.27:
        fail("task-grounded TwoRoom high-noise margin changed")
    if round2(float(summary[("PushT", "0.0")]["semantic_margin_median_mean"])) != -0.58:
        fail("task-grounded PushT base margin changed")


def check_cem_trace_audit_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "cem_trace_audit_20260704.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-cem-trace-audit-0.1":
        fail(f"CEM trace audit schema changed: {meta.get('schema_version')!r}")
    expected_meta = {"n_sequences": 4, "plan_horizon": 5, "action_block": 5, "cem_num_samples": 64, "cem_n_steps": 8, "cem_topk": 8}
    for key, want in expected_meta.items():
        if int(meta.get(key, -1)) != want:
            fail(f"CEM trace audit metadata {key} changed: {meta.get(key)} != {want}")
    rows = data.get("rows", [])
    if len(rows) != 24 or any(row.get("status") != "ok" for row in rows):
        fail("CEM trace audit must contain 24 ok rows")
    got = {(row.get("task"), int(row.get("training_seed")), row.get("std_key")) for row in rows}
    expected = {
        (task, seed, std)
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for seed in (3072, 3073, 3074)
        for std in ("0.0", "0.08")
    }
    if got != expected:
        fail("CEM trace audit row coverage changed")
    summary = {(row["task"], row["std_key"]): row for row in data.get("summary_rows", [])}
    expected_plan = {
        ("TwoRoom", "0.0"): 1.24,
        ("TwoRoom", "0.08"): 0.61,
        ("PushT", "0.0"): 1.96,
        ("PushT", "0.08"): 0.64,
        ("Reacher", "0.0"): 1.15,
        ("Reacher", "0.08"): 0.38,
        ("Cube", "0.0"): 1.30,
        ("Cube", "0.08"): 0.51,
    }
    if set(summary) != set(expected_plan):
        fail(f"CEM trace summary rows mismatch: {sorted(summary)}")
    for key, want in expected_plan.items():
        got_plan = round2(float(summary[key]["final_plan_l2_per_dim_mean_mean"]))
        if got_plan != want:
            fail(f"CEM trace final plan L2/dim changed for {key}: got {got_plan}, want {want}")
    for task in ("TwoRoom", "PushT", "Reacher", "Cube"):
        base = float(summary[(task, "0.0")]["final_plan_l2_per_dim_mean_mean"])
        robust = float(summary[(task, "0.08")]["final_plan_l2_per_dim_mean_mean"])
        if not robust < base:
            fail(f"CEM trace high-noise plan shift no longer below base for {task}: {robust} >= {base}")
    if round2(float(summary[("TwoRoom", "0.08")]["final_seeded_top1_flip_rate_mean"])) != 0.92:
        fail("CEM trace TwoRoom boundary flip rate changed")
    if round2(float(summary[("Reacher", "0.08")]["final_seeded_top1_flip_rate_mean"])) != 0.25:
        fail("CEM trace Reacher high-noise flip rate changed")


def check_three_seed_diagnostic_validation_json() -> None:
    phase0_path = ROOT / "assets" / "paper1_data" / "acpc_phase0_lewm_three_seed.json"
    phase0 = json.loads(phase0_path.read_text(encoding="utf-8"))
    rows = phase0.get("rows", [])
    if len(rows) != 108 or any(row.get("status") != "ok" for row in rows):
        fail("three-seed Phase-0 LeWM artifact must contain 108 ok rows")
    expected = {
        (task, seed, std)
        for task in EXPECTED_TASKS
        for seed in (3072, 3073, 3074)
        for std in EXPECTED_CONFIGS
    }
    got = {(row.get("task"), int(row.get("training_seed")), str(row.get("std_key"))) for row in rows}
    if got != expected:
        fail(f"three-seed Phase-0 coverage mismatch: missing={sorted(expected - got)[:5]}")
    required_fields = {
        "pixels_std0.08_success",
        "pixels_goal_std0.08_success",
        "corruption_drop",
        "acpc_h_norm_by_transition",
        "pcc_abs_median",
        "cra_spearman_mean",
        "maf_flip_rate",
    }
    for row in rows:
        missing = required_fields - set(row)
        if missing:
            fail(f"three-seed Phase-0 row missing fields {missing}: {row.get('task')} {row.get('training_seed')} {row.get('std_key')}")

    validation_path = ROOT / "assets" / "paper1_data" / "three_seed_diagnostic_validation.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    summary = validation.get("summary", {})
    expected_summary = {
        "n_task_seed_blocks": 12,
        "exact_best_hits": 2,
        "within_5pp_hits": 10,
        "checkpoint_candidates_per_block": 8,
    }
    for key, want in expected_summary.items():
        if summary.get(key) != want:
            fail(f"three-seed diagnostic validation {key} mismatch: {summary.get(key)} != {want}")
    if round2(float(summary.get("mean_selected_regret_to_best_pp"))) != 2.25:
        fail("three-seed diagnostic validation mean regret changed")
    splits = {row.get("split"): row for row in validation.get("split_summaries", [])}
    heldout = splits.get("heldout_training_seeds_3073_3074")
    if heldout is None:
        fail("three-seed diagnostic validation missing held-out split summary")
    expected_heldout = {
        "n_task_seed_blocks": 8,
        "n_checkpoint_candidates": 64,
        "exact_best_hits": 0,
        "within_5pp_hits": 7,
    }
    for key, want in expected_heldout.items():
        if heldout.get(key) != want:
            fail(f"three-seed held-out split {key} mismatch: {heldout.get(key)} != {want}")
    if round2(float(heldout.get("mean_selected_regret_to_best_pp"))) != 2.21:
        fail("three-seed held-out split mean regret changed")
    ci = heldout.get("bootstrap_ci95_mean_selected_regret_to_best_pp")
    if [round2(float(v)) for v in ci] != [1.04, 3.54]:
        fail(f"three-seed held-out split CI changed: {ci}")
    selection = validation.get("selection_rows", [])
    if len(selection) != 12:
        fail("three-seed diagnostic validation must contain 12 selection rows")
    if sorted({int(row["training_seed"]) for row in selection}) != [3072, 3073, 3074]:
        fail("three-seed diagnostic validation must cover seeds 3072/3073/3074")


def check_semantic_margin_passrate_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "semantic_margin_passrate_lewm_three_seed.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    if len(rows) != 24 or any(row.get("status") != "ok" for row in rows):
        fail("task-state proxy margin pass-rate artifact must contain 24 ok rows")
    coverage = data.get("coverage", {})
    expected_coverage = {
        f"{task}:{std}": [3072, 3073, 3074]
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for std in ("0.0", "0.08")
    }
    if coverage != expected_coverage:
        fail(f"task-state proxy margin coverage mismatch: {coverage}")
    summary = {(row["task"], row["std_key"]): row for row in data.get("summary_rows", [])}
    expected_pass = {
        ("TwoRoom", "0.0"): 0.44,
        ("TwoRoom", "0.08"): 1.00,
        ("PushT", "0.0"): 0.27,
        ("PushT", "0.08"): 1.00,
        ("Reacher", "0.0"): 0.58,
        ("Reacher", "0.08"): 1.00,
        ("Cube", "0.0"): 0.25,
        ("Cube", "0.08"): 1.00,
    }
    if set(summary) != set(expected_pass):
        fail(f"task-state proxy margin summary rows mismatch: {sorted(summary)}")
    for key, want in expected_pass.items():
        got = round2(float(summary[key]["semantic_margin_pass_rate_mean"]))
        if got != want:
            fail(f"task-state proxy margin pass-rate mismatch for {key}: got {got}, want {want}")



def check_semantic_local_margin_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "semantic_local_margin_lewm_three_seed.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("pair_rule") != "local_task_feature_contrast":
        fail("local task-feature margin artifact must use local_task_feature_contrast")
    if round2(float(meta.get("local_quantile"))) != 0.35:
        fail("local task-feature margin artifact local quantile changed")
    rows = data.get("rows", [])
    if len(rows) != 24 or any(row.get("status") != "ok" for row in rows):
        fail("local task-feature margin artifact must contain 24 ok rows")
    coverage = data.get("coverage", {})
    expected_coverage = {
        f"{task}:{std}": [3072, 3073, 3074]
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for std in ("0.0", "0.08")
    }
    if coverage != expected_coverage:
        fail(f"local task-feature margin coverage mismatch: {coverage}")
    summary = {(row["task"], row["std_key"]): row for row in data.get("summary_rows", [])}
    expected_pass = {
        ("TwoRoom", "0.0"): 0.59,
        ("TwoRoom", "0.08"): 1.00,
        ("PushT", "0.0"): 0.54,
        ("PushT", "0.08"): 1.00,
        ("Reacher", "0.0"): 0.81,
        ("Reacher", "0.08"): 1.00,
        ("Cube", "0.0"): 0.53,
        ("Cube", "0.08"): 1.00,
    }
    if set(summary) != set(expected_pass):
        fail(f"local task-feature margin summary rows mismatch: {sorted(summary)}")
    for key, want in expected_pass.items():
        got = round2(float(summary[key]["semantic_margin_pass_rate_mean"]))
        if got != want:
            fail(f"local task-feature margin pass-rate mismatch for {key}: got {got}, want {want}")
    for key in (("PushT", "0.08"), ("Cube", "0.08")):
        margin = round2(float(summary[key]["semantic_margin_median_mean"]))
        if margin < 18.0:
            fail(f"local task-feature high-noise margin unexpectedly low for {key}: {margin}")


def check_margin_flip_curve_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "margin_flip_curve_lewm_three_seed.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-margin-flip-curve-0.1":
        fail(f"margin flip schema mismatch: {meta.get('schema_version')}")
    if meta.get("seeds") != [3072, 3073, 3074]:
        fail(f"margin flip seeds mismatch: {meta.get('seeds')}")
    if meta.get("tasks") != ["TwoRoom", "PushT", "Reacher", "Cube"]:
        fail(f"margin flip tasks mismatch: {meta.get('tasks')}")
    if meta.get("std_keys") != ["0.0", "0.08"]:
        fail(f"margin flip std keys mismatch: {meta.get('std_keys')}")
    if [round(float(q), 2) for q in meta.get("threshold_quantiles", [])] != [0.0, 0.5, 0.75, 0.9]:
        fail(f"margin flip threshold quantiles mismatch: {meta.get('threshold_quantiles')}")
    rows = data.get("rows", [])
    samples = data.get("sample_rows", [])
    if len(rows) != 96:
        fail(f"margin flip row count mismatch: {len(rows)}")
    if len(samples) != 2400:
        fail(f"margin flip sample row count mismatch: {len(samples)}")
    if any(row.get("status") != "ok" for row in rows):
        fail("margin flip rows contain non-ok status")
    coverage = {
        (row["task"], row["std_key"], round(float(row["threshold_quantile"]), 2), int(row["training_seed"]))
        for row in rows
    }
    expected = {
        (task, std, q, seed)
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for std in ("0.0", "0.08")
        for q in (0.0, 0.5, 0.75, 0.9)
        for seed in (3072, 3073, 3074)
    }
    if coverage != expected:
        fail("margin flip coverage mismatch")
    summary = {
        (row["task"], row["std_key"], round(float(row["threshold_quantile"]), 2)): row
        for row in data.get("summary_rows", [])
    }
    if set(summary) != {
        (task, std, q)
        for task in ("TwoRoom", "PushT", "Reacher", "Cube")
        for std in ("0.0", "0.08")
        for q in (0.0, 0.5, 0.75, 0.9)
    }:
        fail("margin flip summary coverage mismatch")
    expected_q75 = {
        ("TwoRoom", "0.0"): 0.67,
        ("TwoRoom", "0.08"): 0.00,
        ("PushT", "0.0"): 0.92,
        ("PushT", "0.08"): 0.00,
        ("Reacher", "0.0"): 0.79,
        ("Reacher", "0.08"): 0.00,
        ("Cube", "0.0"): 0.84,
        ("Cube", "0.08"): 0.00,
    }
    for key, want in expected_q75.items():
        got = round2(float(summary[(key[0], key[1], 0.75)]["flip_rate_mean"]))
        if got != want:
            fail(f"margin flip q75 mean mismatch for {key}: got {got}, want {want}")
    for task in ("TwoRoom", "PushT", "Reacher", "Cube"):
        base_all = float(summary[(task, "0.0", 0.0)]["flip_rate_mean"])
        robust_all = float(summary[(task, "0.08", 0.0)]["flip_rate_mean"])
        if base_all < 0.75:
            fail(f"margin flip base all-sample flip unexpectedly low for {task}: {base_all}")
        if robust_all > 0.04:
            fail(f"margin flip robust all-sample flip unexpectedly high for {task}: {robust_all}")



def check_unseen_atr_smpr_summary_json() -> None:
    for rel, expected_coverage in {
        "semantic_task_grounded_margin_unseen_blur_lewm_three_seed.json": {
            "TwoRoom:0.0": [3072, 3073, 3074],
            "TwoRoom:0.08": [3072, 3073, 3074],
            "Reacher:0.0": [3072, 3073, 3074],
            "Reacher:0.08": [3072, 3073, 3074],
        },
        "semantic_task_grounded_margin_unseen_resize_lewm_three_seed.json": {
            "PushT:0.0": [3072, 3073, 3074],
            "PushT:0.08": [3072, 3073, 3074],
            "Cube:0.0": [3072, 3073, 3074],
            "Cube:0.08": [3072, 3073, 3074],
        },
    }.items():
        data = json.loads((ROOT / "assets" / "paper1_data" / rel).read_text(encoding="utf-8"))
        meta = data.get("metadata", {})
        if meta.get("pair_rule") != "task_grounded_near_boundary":
            fail(f"{rel} must use task_grounded_near_boundary")
        if round2(float(meta.get("local_quantile"))) != 0.35:
            fail(f"{rel} local quantile changed")
        if data.get("coverage") != expected_coverage:
            fail(f"{rel} coverage mismatch: {data.get('coverage')}")
        if len(data.get("rows", [])) != 12 or any(row.get("status") != "ok" for row in data.get("rows", [])):
            fail(f"{rel} must contain 12 ok rows")

    path = ROOT / "assets" / "paper1_data" / "unseen_atr_smpr_summary_20260707.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-unseen-atr-smpr-summary-20260707-v1":
        fail(f"unseen ATR/SMPR schema changed: {meta.get('schema_version')!r}")
    if "same unseen stressor" not in meta.get("smpr_definition", ""):
        fail("unseen SMPR definition must remain stressor-specific")
    rows = {row.get("task"): row for row in data.get("summary_rows", [])}
    expected = {
        "TwoRoom": (47.67, 90.78, 1.61, 1.24, 0.16, 0.77),
        "Reacher": (22.00, 71.22, 2.81, 0.54, 0.60, 0.98),
        "PushT": (63.44, 66.33, 1.77, 1.53, 0.93, 0.96),
        "Cube": (57.00, 56.11, 1.35, 1.59, 0.98, 0.95),
    }
    if set(rows) != set(expected):
        fail(f"unseen ATR/SMPR summary task coverage changed: {sorted(rows)}")
    for task, want in expected.items():
        row = rows[task]
        got = (
            round2(float(row["baseline_stress_success"]["mean"])),
            round2(float(row["std008_stress_success"]["mean"])),
            round2(float(row["ATR_q90_0.0"]["mean"])),
            round2(float(row["ATR_q90_0.08"]["mean"])),
            round2(float(row["SMPR_0.0"]["mean"])),
            round2(float(row["SMPR_0.08"]["mean"])),
        )
        if got != want:
            fail(f"unseen ATR/SMPR summary {task} changed: got {got}, want {want}")
    corr = data.get("correlations", {})
    if int(corr.get("seed_rows_n", 0)) != 12:
        fail("unseen ATR/SMPR correlations must use 12 seed rows")
    if round2(float(corr.get("spearman_stress_delta_vs_ATR_drop"))) != 0.84:
        fail("unseen ATR-drop Spearman association changed")
    if round2(float(corr.get("spearman_stress_delta_vs_SMPR_gain"))) != 0.87:
        fail("unseen SMPR-gain Spearman association changed")

def check_compressed_metrics_summary_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "compressed_metrics_summary_20260706.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("metadata", {})
    if meta.get("schema_version") != "paper1-compressed-selective-acpc-20260706-v1":
        fail(f"compressed metrics schema changed: {meta.get('schema_version')!r}")
    if meta.get("same_state_metric") != "ATR_q90" or meta.get("selective_metric") != "SMPR_m0":
        fail("compressed metrics must remain ATR_q90 + SMPR_m0")
    rows = data.get("summary_rows", [])
    if len(rows) != 4:
        fail(f"compressed metrics expected 4 summary rows, got {len(rows)}")
    expected = {
        "TwoRoom": (1.509, 0.111, 0.34, 0.99, 68.78, 97.11),
        "PushT": (3.580, 0.247, 0.44, 1.00, 7.22, 85.78),
        "Reacher": (2.628, 0.082, 0.73, 1.00, 18.22, 81.56),
        "Cube": (2.320, 0.100, 0.45, 1.00, 43.11, 62.56),
    }
    row_map = {row.get("task"): row for row in rows}
    if set(row_map) != set(expected):
        fail(f"compressed metrics task coverage changed: {sorted(row_map)}")
    for task, want in expected.items():
        row = row_map[task]
        got = (
            round(float(row["ATR_q90_0.0"]["mean"]), 3),
            round(float(row["ATR_q90_0.08"]["mean"]), 3),
            round(float(row["SMPR_0.0"]["mean"]), 2),
            round(float(row["SMPR_0.08"]["mean"]), 2),
            round(float(row["obs008_success_0.0"]["mean"]), 2),
            round(float(row["obs008_success_0.08"]["mean"]), 2),
        )
        if got != want:
            fail(f"compressed metrics {task} changed: got {got}, want {want}")

def check_target_view_closed_loop_summary_json() -> None:
    path = ROOT / "assets" / "paper1_data" / "target_view_closed_loop_summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    rows = data.get("closed_loop_pixels_std0.08_across_eight_checkpoints")
    expected = {
        "tworoom": (94.708333125, 61.75, 32.958333125),
        "pusht": (72.833333125, 6.749999875, 66.08333325),
        "reacher": (76.166666625, 19.624999875, 56.54166675),
        "cube": (59.83333325, 39.625, 20.20833325),
    }
    if not isinstance(rows, dict) or set(rows) != set(expected):
        fail(
            "target-view summary tasks mismatch: "
            f"expected {sorted(expected)}, got {sorted(rows or {})}"
        )

    for task, want in expected.items():
        row = rows[task]
        got = (
            float(row["full_sequence_mean"]),
            float(row["origin_target_mean"]),
            float(row["full_sequence_advantage"]),
        )
        if any(not approx_equal(g, w) for g, w in zip(got, want)):
            fail(f"target-view closed-loop summary mismatch for {task}: got {got}, want {want}")

    probe = data.get("representative_pusht_0to008", {})
    canonical = probe.get("canonical_seeds_42_43_44", {})
    if canonical.get("full_sequence_pixels_std0.08_raw") != [88.0, 82.0, 89.0]:
        fail("target-view PushT full-sequence canonical raw values changed")
    if canonical.get("origin_target_pixels_std0.08_raw") != [12.0, 4.0, 10.0]:
        fail("target-view PushT origin-target canonical raw values changed")


def check_published_correlations() -> None:
    evals = json.loads((ROOT / "assets" / "paper1_data" / "canonical_evals_20260517.json").read_text(encoding="utf-8"))
    diag = json.loads((ROOT / "assets" / "paper1_data" / "canonical_diagnostics_20260517.json").read_text(encoding="utf-8"))

    predictor = diag["predictor_metrics_by_task"]
    published = diag["published_correlations"]

    metrics = (
        "predictor_target_to_nn_cos_ratio_at_max_std",
        "predictor_rollout_T8_l2_at_max_std",
    )

    for task in sorted(EXPECTED_TASKS):
        std_keys = sorted(evals[task], key=float)
        z = [float(std_key) for std_key in std_keys]
        clean = [float(evals[task][std_key]["metrics"]["clean"]["mean"]) for std_key in std_keys]
        px08 = [
            float(evals[task][std_key]["metrics"]["pixels_std0.08"]["mean"])
            for std_key in std_keys
        ]
        drop = [c - p for c, p in zip(clean, px08)]

        for metric in metrics:
            xs = [float(predictor[task][std_key][metric]) for std_key in std_keys]
            got_pearson = round2(pearson(xs, drop))
            got_spearman = round2(spearman(xs, drop))
            want = published["table4_ood_drop"][task][metric]
            if got_pearson != round2(want["pearson"]) or got_spearman != round2(want["spearman"]):
                fail(
                    f"published Table 4 mismatch for {task}/{metric}: "
                    f"got pearson={got_pearson}, spearman={got_spearman}; "
                    f"want pearson={want['pearson']}, spearman={want['spearman']}"
                )

            got_partial = round2(partial_spearman(xs, drop, z))
            want_partial = published["table4b_partial_spearman_ood_drop_given_std_max"][task][metric]
            if got_partial != round2(want_partial):
                fail(
                    f"published Table 4b mismatch for {task}/{metric}: "
                    f"got partial={got_partial}; want partial={want_partial}"
                )

    push_keys = sorted(evals["PushT"], key=float)
    z = [float(std_key) for std_key in push_keys]
    fragility = [
        float(predictor["PushT"][std_key]["predictor_target_to_nn_cos_ratio_at_max_std"])
        for std_key in push_keys
    ]
    clean = [float(evals["PushT"][std_key]["metrics"]["clean"]["mean"]) for std_key in push_keys]
    px08 = [
        float(evals["PushT"][std_key]["metrics"]["pixels_std0.08"]["mean"])
        for std_key in push_keys
    ]
    drop = [c - p for c, p in zip(clean, px08)]
    table5 = published["table5_pusht_fragility_metric"]["spearman"]
    recomputed = {
        "rho_std_max_metric": round2(spearman(z, fragility)),
        "rho_std_max_clean": round2(spearman(z, clean)),
        "rho_std_max_pixels_std0.08": round2(spearman(z, px08)),
        "rho_std_max_ood_drop": round2(spearman(z, drop)),
        "rho_metric_clean_unconditional": round2(spearman(fragility, clean)),
        "rho_metric_clean_partial_given_std_max": round2(partial_spearman(fragility, clean, z)),
        "rho_metric_pixels_std0.08_unconditional": round2(spearman(fragility, px08)),
        "rho_metric_pixels_std0.08_partial_given_std_max": round2(
            partial_spearman(fragility, px08, z)
        ),
        "rho_metric_ood_drop_unconditional": round2(spearman(fragility, drop)),
        "rho_metric_ood_drop_partial_given_std_max": round2(partial_spearman(fragility, drop, z)),
    }
    for key, got in recomputed.items():
        want = round2(table5[key])
        if got != want:
            fail(f"published Table 5 mismatch for {key}: got {got}, want {want}")


def check_radius_margin_certificate_outputs() -> None:
    summary_path = ROOT / "paper1" / "results" / "radius_margin_certificate_summary.csv"
    gate_path = ROOT / "paper1" / "results" / "radius_margin_gate_ablation.csv"
    boundary_path = ROOT / "paper1" / "results" / "radius_margin_boundary_alignment.csv"
    top1_path = ROOT / "paper1" / "results" / "fixed_pool_top1_agreement.csv"
    summary_rows = list(csv.DictReader(summary_path.open(newline="", encoding="utf-8")))
    gate_rows = list(csv.DictReader(gate_path.open(newline="", encoding="utf-8")))
    boundary_rows = list(csv.DictReader(boundary_path.open(newline="", encoding="utf-8")))
    top1_rows = list(csv.DictReader(top1_path.open(newline="", encoding="utf-8")))

    if len(summary_rows) != 36:
        fail(f"radius-margin summary expected 36 rows, got {len(summary_rows)}")
    if {row["task"] for row in summary_rows} != EXPECTED_TASKS:
        fail("radius-margin summary task set mismatch")
    expected_stdmax_csv = {f"{float(std):.2f}" for std in EXPECTED_CONFIGS}
    if {row["train_stdmax"] for row in summary_rows} != expected_stdmax_csv:
        fail("radius-margin summary stdmax grid mismatch")

    required_columns = {
        "task",
        "train_stdmax",
        "eval_sigma",
        "n_training_seeds",
        "score_clean_mean",
        "score_obs_sigma_0p08_mean",
        "behavioral_plateau_label",
        "atr_q90_mean",
        "clean_margin_q50_mean",
        "cost_drift_q90_mean",
        "certificate_gap_q50_q90_mean",
        "certificate_pass_proxy",
        "candidate_count_mean",
        "notes",
    }
    missing = required_columns - set(summary_rows[0])
    if missing:
        fail(f"radius-margin summary missing columns: {sorted(missing)}")

    for row in summary_rows:
        if row["n_training_seeds"] != "3":
            fail(f"radius-margin summary expected three training seeds: {row}")
        if row["eval_sigma"] != "0.08":
            fail(f"radius-margin summary expected eval_sigma 0.08: {row}")
        if float(row["candidate_count_mean"]) != 65.0:
            fail(f"radius-margin summary expected candidate_count_mean 65.0: {row}")
        for key in (
            "score_clean_mean",
            "score_obs_sigma_0p08_mean",
            "atr_q90_mean",
            "clean_margin_q50_mean",
            "cost_drift_q90_mean",
            "certificate_gap_q50_q90_mean",
        ):
            value = float(row[key])
            if not math.isfinite(value):
                fail(f"radius-margin summary has non-finite {key}: {row}")
        if "Phase-0" in row["notes"] or "artifact" in row["notes"]:
            fail(f"radius-margin summary note uses internal wording: {row['notes']}")

    expected_proxy_ranges = {
        "TwoRoom": ("0.02-0.08", "0.01-0.08", "none", "0.01"),
        "PushT": ("0.02-0.08", "0.03-0.08", "0.02", "none"),
        "Reacher": ("0.04-0.08", "0.02-0.08", "none", "0.02;0.03"),
        "Cube": ("0.03-0.08", "0.03-0.08", "none", "none"),
    }
    proxy_rows = {
        row["task"]: row
        for row in gate_rows
        if row["criterion"] == "fixed-pool cost-margin proxy gap > 0"
    }
    if set(proxy_rows) != EXPECTED_TASKS:
        fail("radius-margin gate missing fixed-pool proxy rows")
    for task, (pred, plateau, fp, fn) in expected_proxy_ranges.items():
        row = proxy_rows[task]
        got = (
            row["predicted_robust_stdmax_range"],
            row["behavioral_plateau_range"],
            row["false_positive_stdmax"],
            row["false_negative_stdmax"],
        )
        if got != (pred, plateau, fp, fn):
            fail(f"radius-margin gate mismatch for {task}: got {got}")
        if "Phase-0" in row["notes"] or "artifact" in row["notes"]:
            fail(f"radius-margin gate note uses internal wording: {row['notes']}")

    joint_rows = [row for row in gate_rows if row["criterion"] == "ATR+SMPR joint gate"]
    if len(joint_rows) != 4:
        fail(f"radius-margin gate expected four ATR+SMPR rows, got {len(joint_rows)}")
    for row in joint_rows:
        if row["predicted_robust_stdmax_range"] != "not computed":
            fail("radius-margin table must not mix the separate ATR/SMPR diagnostic-region audit into the cost-proxy gate row")
        if "reported separately" not in row["notes"] or "cost-proxy table" not in row["notes"]:
            fail(f"radius-margin joint-gate note missing scope explanation: {row['notes']}")
        if "artifact" in row["notes"]:
            fail(f"radius-margin joint-gate note uses internal wording: {row['notes']}")

    expected_boundary = {
        "TwoRoom": ("0.01-0.08", "0.02-0.08", "+0.01", "+0.00", "yes"),
        "PushT": ("0.03-0.08", "0.02-0.08", "-0.01", "+0.00", "yes"),
        "Reacher": ("0.02-0.08", "0.04-0.08", "+0.02", "+0.00", "partial"),
        "Cube": ("0.03-0.08", "0.03-0.08", "+0.00", "+0.00", "yes"),
    }
    if len(boundary_rows) != 4:
        fail(f"boundary alignment expected four rows, got {len(boundary_rows)}")
    for row in boundary_rows:
        task = row["task"]
        got = (
            row["recovery_band"],
            row["diagnostic_proxy_interval"],
            row["start_boundary_error_stdmax"],
            row["end_boundary_error_stdmax"],
            row["within_one_grid_tolerance"],
        )
        if got != expected_boundary.get(task):
            fail(f"boundary alignment mismatch for {task}: got {got}")

    if len(top1_rows) != 12:
        fail(f"fixed-pool top1 audit expected 12 rows, got {len(top1_rows)}")
    top1_map = {(row["task"], row["row_role"]): row for row in top1_rows}
    expected_top1 = {
        ("TwoRoom", "base"): ("0.00", "0.207", "no"),
        ("TwoRoom", "std0.08_endpoint"): ("0.08", "0.960", "yes"),
        ("PushT", "recovery_onset"): ("0.03", "0.937", "yes"),
        ("Reacher", "recovery_onset"): ("0.02", "0.810", "yes"),
        ("Cube", "std0.08_endpoint"): ("0.08", "0.997", "yes"),
    }
    for key, expected in expected_top1.items():
        row = top1_map.get(key)
        if row is None:
            fail(f"fixed-pool top1 audit missing row {key}")
        got = (row["stdmax"], row["empirical_top1_agree"], row["recovery_band_member"])
        if got != expected:
            fail(f"fixed-pool top1 audit mismatch for {key}: got {got}, want {expected}")

    sample_rows = list(csv.DictReader((ROOT / "paper1" / "results" / "sample_level_certificate_full_sweep_audit.csv").open(newline="", encoding="utf-8")))
    if len(sample_rows) != 108:
        fail(f"full-sweep sample-level certificate audit expected 108 rows, got {len(sample_rows)}")
    if any(row.get("status") != "ok" for row in sample_rows):
        fail("full-sweep sample-level certificate audit must have all rows ok")
    sample_alignment = list(csv.DictReader((ROOT / "paper1" / "results" / "sample_level_certificate_recovery_alignment.csv").open(newline="", encoding="utf-8")))
    align = {(row["task"], row["split"]): row for row in sample_alignment}
    all_fragile = align[("ALL", "fragile")]
    all_recovered = align[("ALL", "recovered")]
    got_alignment = (
        round(float(all_fragile["cert_pass_rate_median"]), 2),
        round(float(all_recovered["cert_pass_rate_median"]), 2),
        round(float(all_fragile["top1_flip_rate_median"]), 2),
        round(float(all_recovered["top1_flip_rate_median"]), 2),
    )
    if got_alignment != (0.06, 0.61, 0.54, 0.04):
        fail(f"full-sweep sample-level alignment changed: got {got_alignment}")

    ci_rows = list(csv.DictReader((ROOT / "paper1" / "results" / "sample_level_event_rate_wilson_ci.csv").open(newline="", encoding="utf-8")))
    if len(ci_rows) != 30:
        fail(f"sample-level Wilson CI expected 30 rows, got {len(ci_rows)}")
    ci = {(row["task"], row["split"], row["metric"]): row for row in ci_rows}
    got_ci = (
        round(float(ci[("ALL", "fragile", "cert-pass")]["rate"]), 2),
        round(float(ci[("ALL", "recovered", "cert-pass")]["rate"]), 2),
        round(float(ci[("ALL", "fragile", "top-1 flip")]["rate"]), 2),
        round(float(ci[("ALL", "recovered", "top-1 flip")]["rate"]), 2),
        round(float(ci[("ALL", "fragile", "top-1 flip | cert-pass")]["rate"]), 2),
        round(float(ci[("ALL", "recovered", "top-1 flip | cert-pass")]["rate"]), 2),
        int(ci[("ALL", "fragile", "top-1 flip | cert-pass")]["n"]),
        int(ci[("ALL", "recovered", "top-1 flip | cert-pass")]["n"]),
    )
    if got_ci != (0.20, 0.61, 0.53, 0.06, 0.00, 0.00, 678, 4479):
        fail(f"sample-level Wilson CI rates changed: got {got_ci}")

    sensitivity_rows = list(csv.DictReader((ROOT / "paper1" / "results" / "gaussian_sensitivity_summary.csv").open(newline="", encoding="utf-8")))
    if len(sensitivity_rows) != 12:
        fail(f"Gaussian sensitivity summary expected 12 rows, got {len(sensitivity_rows)}")
    sens = {(row["task"], row["checkpoint_type"]): row for row in sensitivity_rows}
    expected_sens = {"TwoRoom": 0.003, "PushT": 0.008, "Reacher": 0.002, "Cube": 0.008}
    for task, expected in expected_sens.items():
        got = round(float(sens[(task, "endpoint")]["sensitivity_slope_vs_base"]), 3)
        if got != expected:
            fail(f"Gaussian sensitivity endpoint/base changed for {task}: got {got}, want {expected}")

    jvp_rows = list(csv.DictReader((ROOT / "paper1" / "results" / "jvp_hutchinson_sensitivity_audit.csv").open(newline="", encoding="utf-8")))
    if len(jvp_rows) != 36:
        fail(f"JVP/Hutchinson audit expected 36 rows, got {len(jvp_rows)}")
    if any(row.get("status") != "ok" for row in jvp_rows):
        fail("JVP/Hutchinson audit must have all rows ok")
    if sorted({row.get("n_sequences") for row in jvp_rows}) != ["100"] or sorted({row.get("hutchinson_probes") for row in jvp_rows}) != ["8"]:
        fail("JVP/Hutchinson audit must use n_sequences=100 and hutchinson_probes=8")
    jvp_summary = list(csv.DictReader((ROOT / "paper1" / "results" / "jvp_hutchinson_sensitivity_summary.csv").open(newline="", encoding="utf-8")))
    if len(jvp_summary) != 12:
        fail(f"JVP/Hutchinson summary expected 12 rows, got {len(jvp_summary)}")
    jvp = {(row["task"], row["checkpoint_type"]): row for row in jvp_summary}
    expected_jvp_composed = {"TwoRoom": 0.003, "PushT": 0.010, "Reacher": 0.006, "Cube": 0.026}
    expected_jvp_encoder = {"TwoRoom": 0.003, "PushT": 0.017, "Reacher": 0.003, "Cube": 0.023}
    for task, expected in expected_jvp_composed.items():
        got = round(float(jvp[(task, "endpoint")]["composed_trace_per_pixel_dim_vs_base"]), 3)
        if got != expected:
            fail(f"JVP/Hutchinson composed endpoint/base changed for {task}: got {got}, want {expected}")
    for task, expected in expected_jvp_encoder.items():
        got = round(float(jvp[(task, "endpoint")]["encoder_trace_per_pixel_dim_vs_base"]), 3)
        if got != expected:
            fail(f"JVP/Hutchinson encoder endpoint/base changed for {task}: got {got}, want {expected}")

    guard_rows = list(csv.DictReader((ROOT / "paper1" / "results" / "joint_guard_side_validation.csv").open(newline="", encoding="utf-8")))
    if len(guard_rows) != 10:
        fail(f"joint guard-side validation expected 10 rows, got {len(guard_rows)}")
    guard = {(row["task"], row["split"]): row for row in guard_rows}
    all_guard_fragile = guard[("ALL", "fragile")]
    all_guard_recovered = guard[("ALL", "recovered")]
    got_guard = (
        round(float(all_guard_fragile["atr_normalized_q90_median"]), 2),
        round(float(all_guard_recovered["atr_normalized_q90_median"]), 2),
        round(float(all_guard_fragile["smpr_delta0_median"]), 2),
        round(float(all_guard_recovered["smpr_delta0_median"]), 2),
        round(float(all_guard_fragile["fixed_pool_top1_flip_median"]), 2),
        round(float(all_guard_recovered["fixed_pool_top1_flip_median"]), 2),
    )
    if got_guard != (0.84, 0.09, 0.86, 1.00, 0.54, 0.04):
        fail(f"joint guard-side validation changed: got {got_guard}")

    for rel in (
        "assets/paper1_figs/fig_radius_margin_interval_overlay.png",
        "assets/paper1_figs/fig_radius_margin_overlap.png",
        "assets/paper1_figs/fig_endpoint_atr_smpr.png",
        "assets/paper1_figs/fig_fixed_pool_event_rates.png",
        "assets/paper1_figs/fig_gaussian_sensitivity_main.png",
        "assets/paper1_figs/fig_jvp_trace_decomposition_heatmap.png",
        "assets/paper1_figs/fig_full_sweep_planner_guard.png",
    ):
        path = ROOT / rel
        if path.stat().st_size < 10_000:
            fail(f"paper1 figure looks too small: {rel}")


def check_claim_aligned_three_pillar_evidence() -> None:
    """Validate the current three-seed P1, all-subset P2, and final-rule P3."""

    p1 = _load_strict_json(
        ROOT / "paper1/results/future_drift_three_seed_summary_v1.json"
    )
    if p1.get("training_seeds") != [3072, 3073, 3074]:
        fail("P1 training-seed set changed")
    if p1.get("all_seed_task_cells_pass") is not True:
        fail("P1 must preserve direction on all 12 task-seed cells")
    for key, expected in (
        ("mean_reduction_vs_one_step", 0.5589057064173736),
        ("sample_sd_reduction_vs_one_step", 0.047338259788311327),
        ("mean_reduction_vs_same_horizon_control", 0.5129276774853404),
        ("sample_sd_reduction_vs_same_horizon_control", 0.03524693071442968),
    ):
        if not math.isclose(float(p1[key]), expected, abs_tol=1e-12):
            fail(f"P1 three-seed statistic changed: {key}")

    p2 = _load_strict_json(
        ROOT / "paper1/results/cross_task_atr_smpr_all_subsets_summary_v1.json"
    )
    if p2.get("schema_version") != "paper1-cross-task-selective-rule-summary-1.0":
        fail("P2 all-subset schema changed")
    if (
        p2.get("partition_count") != 14
        or p2.get("detail_row_count") != 84
        or p2.get("evaluation_task_incidence_count") != 28
        or p2.get("partitions_are_independent_samples") is not False
    ):
        fail("P2 all-subset coverage changed")
    coverage = {row["source_coverage"]: row for row in p2["coverage"]}
    for source_count, expected_ba, expected_onset in (
        (1, 0.8397156084656084, 0.01111111111111111),
        (2, 0.8552248677248677, 0.009722222222222222),
        (3, 0.8540674603174603, 0.01),
    ):
        row = coverage[source_count]
        if not math.isclose(row["balanced_accuracy"], expected_ba, abs_tol=1e-12):
            fail(f"P2 balanced accuracy changed for {source_count} source tasks")
        if not math.isclose(row["mean_abs_start_error"], expected_onset, abs_tol=1e-12):
            fail(f"P2 onset error changed for {source_count} source tasks")

    p3 = _load_strict_json(
        ROOT
        / "paper1/results/external_validation/"
        "cross_stressor_three_source_thresholds_summary_v1.json"
    )
    if p3.get("threshold_search_on_blur_or_resize") is not False:
        fail("P3 must not select thresholds on blur or resize")
    overall = p3["overall"]
    if overall.get("n") != 24 or overall.get("discordant_n") != 2:
        fail("P3 pair coverage changed")
    if not math.isclose(
        overall["balanced_accuracy"], 0.8888888888888888, abs_tol=1e-12
    ) or not math.isclose(
        overall["spearman_delta_behavior_vs_delta_selective_score"],
        0.9093153287220684,
        abs_tol=1e-12,
    ):
        fail("P3 final selective-score transfer changed")

    main_text = (ROOT / "paper1/main.tex").read_text(encoding="utf-8")
    lowered = main_text.lower()
    for token in (
        "seed3075",
        "seed 3075",
        "dev-era",
        "correct-action",
        "tables/table_seed_transfer_audit",
        "tables/table_cross_stressor_robustness_audit",
    ):
        if token in lowered:
            fail(f"retired paper-facing token restored: {token}")
    for token in (
        "def:selective-discriminability",
        "fig_future_drift_three_seed_v1.pdf",
        "fig_cross_task_atr_smpr_source_coverage_v1.pdf",
        "fig_cross_stressor_selective_transfer_v1.pdf",
        "tables/table_cross_task_atr_smpr_all_subsets_v1",
        "tables/table_cross_stressor_all_pairs_v1",
    ):
        if token not in main_text:
            fail(f"current Paper1 mainline is missing: {token}")

    for rel in (
        "assets/paper1_figs/fig_future_drift_three_seed_v1.pdf",
        "assets/paper1_figs/fig_cross_task_atr_smpr_source_coverage_v1.pdf",
        "assets/paper1_figs/fig_cross_stressor_selective_transfer_v1.pdf",
    ):
        if (ROOT / rel).stat().st_size < 5_000:
            fail(f"current Paper1 figure looks too small: {rel}")


def check_public_v1_remediation_artifacts() -> None:
    """Validate the frozen V1 evidence and its deliberately weak claim scope."""

    for rel, expected_hash in PUBLIC_V1_ARTIFACT_HASHES.items():
        path = ROOT / rel
        got_hash = _sha256_file(path)
        if got_hash != expected_hash:
            fail(f"public-v1 artifact hash changed for {rel}: got {got_hash}, want {expected_hash}")

    manifest_text = (ROOT / "DATA_MANIFEST.md").read_text(encoding="utf-8")
    for rel, expected_hash in PUBLIC_V1_ARTIFACT_HASHES.items():
        if rel not in manifest_text or expected_hash not in manifest_text:
            fail(f"DATA_MANIFEST.md is missing public-v1 hash entry for {rel}")

    diagnostic_manifest = _load_strict_json(ROOT / "paper1/results/diagnostic_manifest.json")
    if diagnostic_manifest.get("schema_version") != "paper1-diagnostic-manifest-2.0":
        fail("diagnostic manifest is not the public-v1 v2 manifest")
    if diagnostic_manifest.get("frozen_protocol_sha256") != FROZEN_PROTOCOL_SHA256:
        fail("diagnostic manifest frozen protocol hash changed")
    if diagnostic_manifest.get("external_threshold_search") is not False:
        fail("diagnostic manifest must prohibit external threshold search")
    if diagnostic_manifest.get("public_v1_artifact_sha256") != PUBLIC_V1_ARTIFACT_HASHES:
        fail("diagnostic manifest public-v1 hash map does not match the release contract")

    def checked_external(rel: str) -> dict:
        payload = _load_strict_json(ROOT / rel)
        metadata = payload.get("metadata", {})
        if metadata.get("protocol_hash") != FROZEN_PROTOCOL_SHA256:
            fail(f"{rel} does not record the frozen protocol hash")
        if metadata.get("missing_rows", []) or metadata.get("errors", []):
            fail(f"{rel} contains missing rows or errors")
        if metadata.get("status", "complete") != "complete":
            fail(f"{rel} is not complete")
        return payload

    e1 = checked_external("paper1/results/frozen_external_validation_summary_v3.json")
    e1_metrics = e1["metrics"]
    if e1_metrics.get("num_rows") != 72:
        fail("E1 strict held-out LeWM validation must contain 72 rows")
    if not math.isclose(e1_metrics["balanced_accuracy"], 0.9445454545454546, abs_tol=1e-12):
        fail("E1 balanced accuracy changed")
    if not math.isclose(e1_metrics["auprc"], 0.9654813594276511, abs_tol=1e-12):
        fail("E1 AUPRC changed")

    with (
        ROOT / "paper1/results/external_validation/pldm_frozen_rows_v2.csv"
    ).open(newline="", encoding="utf-8") as stream:
        e2_rows = list(csv.DictReader(stream))
    if len(e2_rows) != 36:
        fail("E2 PLDM architecture audit must contain one complete 36-row family")
    if {row["model_family"] for row in e2_rows} != {"PLDM"}:
        fail("E2 architecture audit contains a non-PLDM row")
    if {row["task"] for row in e2_rows} != {"TwoRoom", "PushT", "Reacher", "Cube"}:
        fail("E2 PLDM architecture audit has incomplete task coverage")
    e2_table = (
        ROOT / "paper1/tables/table_pldm_architecture_portability.tex"
    ).read_text(encoding="utf-8")
    for expected in (
        "PLDM thresholds, other three tasks & 0.836 & 0.789 & 0.882 & 4 & 2",
        "LeWM thresholds, PLDM-normalized & 0.807 & 0.778 & 0.824 & 4 & 3",
        "raw thresholds are not assumed to match across model families",
    ):
        if expected not in e2_table:
            fail(f"E2 PLDM architecture-portability table changed: {expected}")

    e3 = checked_external("paper1/results/external_validation/cross_stressor_fixed_rho_summary.json")
    e3_meta = e3["metadata"]
    if e3_meta.get("schema_version") != "paper1-cross-stressor-fixed-rho-1.2":
        fail("E3 does not contain the paired-change schema")
    if (
        e3_meta.get("paired_change_threshold_search_allowed") is not False
        or e3_meta.get("paired_change_zero_threshold") != 0.0
        or e3_meta.get("robustness_audit_post_freeze") is not True
        or e3_meta.get("robustness_audit_threshold_search_allowed") is not False
        or e3_meta.get("absolute_calibration_scope") != "model-family-specific"
    ):
        fail("E3 paired-change/robustness-audit/family-calibration contract changed")

    if e3_meta.get("severity_search_allowed") is not False or e3_meta.get("rho_unique_values") != [0.08]:
        fail("E3 must be a fixed-rho, no-severity-search boundary test")
    fixed_counts = e3["count_contract"]["fixed_endpoint_rows"]
    pair_counts = e3["count_contract"]["all_base_to_endpoint_pairs"]
    if fixed_counts.get("observed_total") != fixed_counts.get("expected_total") or fixed_counts.get("observed_total") != 16:
        fail("E3 fixed-endpoint rows are incomplete")
    if pair_counts.get("observed_total") != pair_counts.get("expected_total") or pair_counts.get("observed_total") != 32:
        fail("E3 base-to-endpoint pairs are incomplete")
    if not math.isclose(e3["fixed_endpoint_metrics"]["balanced_accuracy"], 0.5625, abs_tol=1e-12):
        fail("E3 fixed-rho balanced accuracy changed")

    paired = e3["paired_change"]
    if "reference checkpoint" not in paired.get("scope", ""):
        fail("E3 paired-change scope must require a reference checkpoint")
    if "zero threshold" not in paired.get("threshold_contract", ""):
        fail("E3 paired-change contract must share one zero threshold")
    lewm_paired = paired["by_model_family"]["LeWM"]["diagnostics"]["joint_score"]
    for field, expected in (
        ("n", 24),
        ("balanced_accuracy", 0.8888888888888888),
        ("auprc", 0.9739334195216549),
        ("precision", 0.8823529411764706),
        ("recall", 1.0),
        ("spearman_delta_behavior_vs_oriented_delta_score", 0.8641009119252958),
        ("signed_agreement_delta_behavior_vs_oriented_delta_score", 0.9166666666666666),
    ):
        value = lewm_paired.get(field)
        if isinstance(expected, int):
            if value != expected:
                fail(f"E3 LeWM paired-change {field} changed")
        elif not math.isclose(float(value), expected, abs_tol=1e-12):
            fail(f"E3 LeWM paired-change {field} changed")
    lewm_stressors = paired["by_model_family"]["LeWM"]["joint_by_stressor"]
    if not math.isclose(lewm_stressors["blur"]["balanced_accuracy"], 0.875, abs_tol=1e-12):
        fail("E3 LeWM blur paired-change balanced accuracy changed")
    if not math.isclose(lewm_stressors["resize"]["balanced_accuracy"], 0.9, abs_tol=1e-12):
        fail("E3 LeWM resize paired-change balanced accuracy changed")

    all_diagnostics = paired["all_rows"]["diagnostics"]
    expected_spearman = {
        "encoder_q90": 0.8649986288735068,
        "atr_h8_q90": 0.8618825075149881,
        "time_shuffled_h8_q90": 0.8739803904362959,
        "joint_score": 0.8708642690777773,
    }
    for diagnostic, expected in expected_spearman.items():
        value = all_diagnostics[diagnostic][
            "spearman_delta_behavior_vs_oriented_delta_score"
        ]
        if not math.isclose(value, expected, abs_tol=1e-12):
            fail(f"E3 paired diagnostic Spearman changed: {diagnostic}")

    bootstrap = paired["lewm_block_bootstrap"]
    if (
        bootstrap.get("block_count") != 12
        or bootstrap.get("repetitions") != 5000
        or bootstrap.get("seed") != 20260711
        or bootstrap.get("stressors_retained_within_block") != ["blur", "resize"]
    ):
        fail("E3 LeWM paired-change bootstrap contract changed")
    expected_intervals = {
        "balanced_accuracy": [0.7, 1.0],
        "auprc": [0.8693029143475574, 1.0],
        "spearman_delta_behavior_vs_oriented_delta_score": [
            0.6411715871413971,
            0.9319301469909482,
        ],
        "signed_agreement_delta_behavior_vs_oriented_delta_score": [
            0.7916666666666666,
            1.0,
        ],
    }
    for field, expected in expected_intervals.items():
        observed = bootstrap["metrics"][field]["ci95"]
        if any(
            not math.isclose(float(value), target, abs_tol=1e-12)
            for value, target in zip(observed, expected)
        ):
            fail(f"E3 paired-change bootstrap interval changed: {field}")


    audit = paired["lewm_robustness_audit"]
    exact = audit["exact_randomization"]
    if (
        exact.get("block_count") != 12
        or exact.get("enumerated_assignments") != 4096
        or not math.isclose(exact["observed_spearman"], 0.8641009119252958, abs_tol=1e-12)
        or not math.isclose(exact["one_sided_p_value"], 0.000244140625, abs_tol=1e-15)
        or not math.isclose(exact["two_sided_p_value"], 0.00048828125, abs_tol=1e-15)
    ):
        fail("E3 exact block sign-flip audit changed")
    row_agreement = exact["row_level_signed_agreement"]
    if row_agreement.get("successes") != 22 or row_agreement.get("trials") != 24:
        fail("E3 signed-agreement count changed")

    expected_deletion_spearman = {
        "leave_one_task_out": [0.74754785387991, 0.8972639295879029],
        "leave_one_training_seed_out": [0.7529411764705882, 0.9403976055841533],
    }
    for key, expected in expected_deletion_spearman.items():
        observed = audit["deletion_stability"][key]["remaining_metric_range"][
            "spearman"
        ]
        if any(
            not math.isclose(float(value), target, abs_tol=1e-12)
            for value, target in zip(observed, expected)
        ):
            fail(f"E3 deletion-stability Spearman range changed: {key}")

    joint_selection = audit["selection_by_diagnostic"]["joint_score"]
    for field, expected in (
        ("choice_accuracy", 0.9166666666666666),
        ("material_choice_accuracy", 1.0),
        ("mean_regret_pp", 0.13888887500000013),
        ("max_regret_pp", 2.333333000000003),
    ):
        if not math.isclose(float(joint_selection[field]), expected, abs_tol=1e-12):
            fail(f"E3 joint selection audit changed: {field}")
    failure_map = audit["joint_failure_map"]
    if (
        failure_map.get("count") != 2
        or any(row.get("behavior_class") != "neutral" for row in failure_map["rows"])
        or any(not math.isclose(row.get("delta_behavior"), 4.0, abs_tol=1e-12) for row in failure_map["rows"])
        or any(not math.isclose(row.get("selection_regret_pp"), 0.0, abs_tol=1e-12) for row in failure_map["rows"])
    ):
        fail("E3 joint failure map changed")

    incremental = audit["incremental_block_bootstrap"]
    if (
        incremental.get("block_count") != 12
        or incremental.get("repetitions") != 5000
        or incremental.get("seed") != 20260712
    ):
        fail("E3 incremental bootstrap contract changed")
    for diagnostic in (
        "encoder_q90",
        "h1_q90",
        "atr_h8_q90",
        "time_shuffled_h8_q90",
    ):
        interval = incremental["comparisons"][diagnostic]["metrics"][
            "delta_spearman_joint_minus_comparator"
        ]["ci95"]
        if not (float(interval[0]) <= 0.0 <= float(interval[1])):
            fail(
                "E3 must retain the no-unique-joint-increment boundary for "
                f"{diagnostic}"
            )

    e4 = checked_external("paper1/results/external_validation/target_view_frozen_summary.json")
    e4_meta = e4["metadata"]
    if e4_meta.get("threshold_search_allowed") is not False:
        fail("E4 must prohibit threshold search")
    counts = e4["count_contract"]
    if counts.get("observed_rows") != counts.get("expected_rows") or counts.get("observed_rows") != 64:
        fail("E4 target-view/full-sequence rows are incomplete")
    full_gate = e4["branch_metrics"]["full_sequence"]["frozen_gate"]
    target_gate = e4["branch_metrics"]["target_view"]["frozen_gate"]
    if full_gate.get("false_pass_rate", 0.0) < 0.70 or target_gate.get("positive_n") != 0:
        fail("E4 no longer records the failed-repair boundary described in the paper")

    baselines = _load_strict_json(ROOT / "paper1/results/diagnostic_baselines/diagnostic_baseline_all_v1.json")
    baseline_rows = baselines.get("rows", [])
    baseline_meta = baselines.get("metadata", {})
    if len(baseline_rows) != 272 or baseline_meta.get("status_counts") != {"ok": 272}:
        fail("matched diagnostic baseline benchmark must contain 272 ok rows")
    if baseline_meta.get("external_threshold_search_allowed") is not False:
        fail("matched diagnostic baselines must not tune on external rows")
    if any(row.get("status") != "ok" or row.get("reference_atr_match") is not True for row in baseline_rows):
        fail("matched diagnostic baseline rows are incomplete or use a mismatched ATR map")

    rho = _load_strict_json(ROOT / "paper1/results/diagnostic_baselines/gaussian_rho_confound_summary.json")
    rho_meta = rho.get("metadata", {})
    if rho_meta.get("external_leaderboard_eligible") is not False:
        fail("privileged Gaussian rho audit must be excluded from external leaderboards")
    if rho["count_contract"].get("observed_rows") != rho["count_contract"].get("expected_rows"):
        fail("Gaussian rho confound audit rows are incomplete")

    jvp = _load_strict_json(ROOT / "paper1/results/jvp_hutchinson_sensitivity_audit_v2.json")
    if len(jvp.get("rows", [])) != 36 or len(jvp.get("probe_rows", [])) != 288:
        fail("JVP v2 audit must contain 36 checkpoint rows and 288 probes")
    if jvp["metadata"].get("status_counts") != {"ok": 36}:
        fail("JVP v2 audit is incomplete")
    for row in jvp["rows"]:
        kappa_sub = float(row["kappa_submultiplicative"])
        kappa_rel = float(row["kappa_relative_isotropic"])
        latent_dim = int(row["latent_input_dim"])
        if kappa_sub > 1.0 + 1e-9:
            fail("bounded kappa_submultiplicative exceeds one")
        if not math.isclose(kappa_rel, latent_dim * kappa_sub, rel_tol=1e-9, abs_tol=1e-12):
            fail("kappa_relative_isotropic is not latent_dim * kappa_submultiplicative")

    linear = _load_strict_json(ROOT / "paper1/results/linearization_horizon_sensitivity_v1.json")
    linear_meta = linear["metadata"]
    if linear_meta.get("frozen_protocol_sha256") != FROZEN_PROTOCOL_SHA256:
        fail("linearization audit does not record the frozen protocol hash")
    expected_counts = {
        "checkpoint_rows": 36,
        "calibration_rows": 144,
        "horizon_rows": 432,
        "probe_rows": 288,
    }
    for key, expected in expected_counts.items():
        if len(linear.get(key, [])) != expected:
            fail(f"linearization audit {key} count changed")
    if linear_meta.get("horizons") != [1, 2, 4, 8] or linear_meta.get("quantiles") != [0.8, 0.9, 0.95]:
        fail("linearization audit H/q sensitivity grid changed")
    if linear_meta.get("small_sigmas") != [0.0025, 0.005, 0.01, 0.02]:
        fail("linearization audit small-sigma calibration grid changed")

    cert = _load_strict_json(ROOT / "paper1/results/fixed_pool_candidatewise_certificate_summary.json")
    if cert.get("count_contract") != {
        "checkpoint_rows": 108,
        "k_sensitivity_rows": 432,
        "risk_coverage_rows": 7,
        "sample_rows": 10800,
    }:
        fail("sharp fixed-pool certificate count contract changed")
    overall = cert["overall"]
    if overall.get("sharp_cert_invariant_flip_count") != 0:
        fail("sharp certificate deterministic invariant failed")
    if not math.isclose(overall["sharp_cert_pass_rate"], 0.7003703703703704, abs_tol=1e-12):
        fail("sharp certificate coverage changed")
    bootstrap = cert["hierarchical_block_bootstrap"]
    if bootstrap.get("block_count") != 12 or bootstrap.get("repetitions") != 2000:
        fail("sharp certificate hierarchical uncertainty contract changed")

    sensitivity = _load_strict_json(ROOT / "assets/paper1_data/smpr_sensitivity_v2.json")
    if sensitivity["count_contract"].get("total_rows") != 912:
        fail("SMPR sensitivity grid must contain 912 rows")
    controls = _load_strict_json(ROOT / "assets/paper1_data/smpr_controls_v2.json")
    gates = controls["correctness_gates"]
    decisions = controls["claim_decisions"]
    if gates.get("constant_collapse_rejected_all_mve_rows") is not True:
        fail("SMPR constant-collapse correctness gate failed")
    for key in (
        "action_relevance_increment_established",
        "progressive_collapse_sensitivity_established",
        "task_grounded_increment_established",
    ):
        if decisions.get(key) is not False:
            fail(f"SMPR release claim decision changed: {key}")
    oracle = _load_strict_json(ROOT / "assets/paper1_data/smpr_oracle_guard_v2.json")
    if oracle["count_contract"].get("observed_rows") != 4:
        fail("TwoRoom+PushT state-derived SMPR MVE must contain four rows")
    if oracle["metadata"].get("pusht_simulator_goal_state_available_in_hdf5") is not False:
        fail("PushT MVE must disclose the missing simulator goal state")

    references = (ROOT / "paper1/references.bib").read_text(encoding="utf-8")
    reference_audit = (ROOT / "paper1/docs/reference_audit.md").read_text(encoding="utf-8")
    for key, arxiv_id in (
        ("yan2026mwm", "2603.07799"),
        ("chen2026atm", "2606.09028"),
        ("zhang2026deltajepa", "2606.31232"),
        ("seo2026acid", "2607.02403"),
        ("ruan2026futurecompatible", "2605.07514"),
        ("schaefer2026kinematic", "2607.05966"),
    ):
        if "{" + key + "," not in references or arxiv_id not in references or arxiv_id not in reference_audit:
            fail(f"concurrent reference/audit is incomplete for {key}")

    runner = (ROOT / "paper1/scripts/run_all_paper1_diagnostics.sh").read_text(encoding="utf-8")
    for shard in (
        "run_jvp_hutchinson_shards.sh",
        "run_diagnostic_baseline_shards.sh",
        "run_fixed_pool_certificate_shards.sh",
        "run_smpr_controls_mve.sh",
        "run_linearization_horizon_shards.sh",
    ):
        if shard not in runner:
            fail(f"serial remediation runner is missing {shard}")
    if "PAPER1_DIAGNOSTIC_THREADS" not in runner or "python -m tools.paper1_sample_level_certificate" in runner:
        fail("run_all_paper1_diagnostics.sh restored the retired unbounded checkpoint path")

    trainer = (ROOT / "run_trainer.sh").read_text(encoding="utf-8")
    for token in (
        'eval_max_concurrency="${eval_max_concurrency:-1}"',
        'eval_timeout_seconds="${eval_timeout_seconds:-0}"',
        'eval_resume="${eval_resume:-0}"',
        'eval.save_video=${eval_save_video_bool}',
        'timeout --signal=TERM --kill-after=60s',
        'python -u eval.py',
    ):
        if token not in trainer:
            fail(f"run_trainer.sh is missing bounded/resumable eval control: {token}")
    eval_source = (ROOT / "eval.py").read_text(encoding="utf-8")
    for token in ("np.maximum.at(max_step, inverse, step_idx)", 'cfg.eval.get("save_video", False)', "flush=True"):
        if token not in eval_source:
            fail(f"eval.py is missing progress/performance control: {token}")


def main() -> int:
    checks = [
        ("artifacts", check_artifacts),
        ("paired multi-severity protocol", check_paired_multiseverity_protocol),
        ("public-v1 remediation artifacts", check_public_v1_remediation_artifacts),
        ("current selective diagnostic evidence", check_claim_aligned_three_pillar_evidence),
        ("forbidden text", check_forbidden_text),
        ("appendix internal heading gate", check_appendix_internal_heading_gate),
        ("visual and text structure", check_visual_text_structure),
        ("canonical json", check_canonical_json),
        ("pldm canonical json", check_pldm_canonical_json),
        ("canonical diagnostics json", check_canonical_diagnostics_json),
        ("pldm diagnostics json", check_pldm_diagnostics_json),
        ("pldm full diagnostics json", check_pldm_full_diagnostics_json),
        ("acpc phase0 diagnostics json", check_acpc_phase0_diagnostics_json),
        ("remediation phase1 smoke v2", check_remediation_phase1_smoke_v2),
        ("blur baselines json", check_blur_baselines_json),
        ("acpc basin json", check_acpc_basin_json),
        ("pldm acpc basin json", check_pldm_acpc_basin_json),
        ("compressed metrics summary json", check_compressed_metrics_summary_json),
        ("radius-margin certificate outputs", check_radius_margin_certificate_outputs),
        ("unseen ATR/SMPR summary json", check_unseen_atr_smpr_summary_json),
        ("target-view closed-loop json", check_target_view_closed_loop_summary_json),
        ("training-seed Gaussian lockbox json", check_training_seed_gaussian_lockbox_json),
        ("three-seed Gaussian sweep summary json", check_three_seed_gaussian_sweep_summary_json),
        ("three-seed diagnostic validation json", check_three_seed_diagnostic_validation_json),
        ("selector-baseline audit json", check_selector_baseline_audit_json),
        ("selector plateau audit json", check_selector_plateau_audit_json),
        ("residual diagnostic audit json", check_residual_diagnostic_audit_json),
        ("selector incremental audit json", check_selector_incremental_audit_json),
        ("margin-conditioned flip json", check_margin_flip_curve_json),
        ("task-state proxy margin pass-rate json", check_semantic_margin_passrate_json),
        ("local task-feature margin json", check_semantic_local_margin_json),
        ("task-grounded semantic margin json", check_semantic_task_grounded_margin_json),
        ("CEM trace audit json", check_cem_trace_audit_json),
        ("prospective validation summary json", check_prospective_validation_summary_json),
        ("prospective ATR/SMPR validation", check_prospective_atr_smpr_validation),
        ("external baselines json", check_external_baselines_json),
        ("pldm correlations json", check_pldm_correlations_json),
        ("partial-corr bootstrap json", check_partial_corr_bootstrap_json),
        ("published correlations", check_published_correlations),
    ]
    for name, fn in checks:
        try:
            fn()
        except AssertionError as exc:
            print(f"[FAIL] {name}: {exc}", file=sys.stderr)
            return 1
        print(f"[OK] {name}")
    print("[OK] paper1 release consistency checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
