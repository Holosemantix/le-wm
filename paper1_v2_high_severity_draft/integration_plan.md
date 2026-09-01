# Minimal integration plan

The scientific argument should be unified, while the two experiments remain
visibly separate. The v1 numerical results do not need to be rerun or replaced.

## Main-paper changes

| Current location in `paper1/main.tex` | Action | Purpose |
|---|---|---|
| Abstract | Preserve the concise v1 abstract | The broad-severity experiment strengthens an existing checkpoint-level claim but does not change the central contribution or strongest headline result |
| Introduction, current lines 211--216 | Replace the general “Together” statement | State the regime-dependent roles of IR and SR |
| Evaluation protocol, after current line 722 | Add one compact protocol paragraph | Identify the extension as a separate 8-by-4 experiment with unchanged diagnostics |
| After the moderate-severity recovery result | Delete the forced-collapse result and insert `main_text_extension.tex` | Replace the artificial stress case with SR activation in ordinarily trained high-severity checkpoints and a behavioral association |
| Current line 1030 | Keep the threshold-grid edge limitation | The extension broadens training/evaluation severity but does not test IR thresholds above 0.3 |
| Discussion, current lines 1108--1123 | Replace two paragraphs | Connect moderate-regime nonbinding SR with its observed high-severity activation; retain collapse only as a definition-level counterexample |
| Scope/future work, current lines 1131--1142 | Replace repeated limitations | Remove “multiple severities” as future work; keep nominal-quality and selector-utility boundaries |
| Conclusion, current lines 1153--1157 | Replace checkpoint-level summary | Report the broader regime without claiming selection utility |

## Appendix changes

Insert `appendix_extension.tex` after the existing threshold protocol. It adds:

- the factorial aggregation convention;
- exact direct and exposure-adjusted associations;
- a retention-ratio sensitivity result;
- an explicit statement that no row-level population inference is made.

Delete the controlled SIGReg-collapse subsection and
`tab:sigreg-collapse-control`. The method section already states the constant-
representation counterexample, while the broad-severity extension supplies the
reader-facing empirical evidence for SR.

Copy the generated `multiseverity_numbers.tex` alongside the appendix table and
load it before the new subsection. This keeps every reported count and
association tied to the frozen source hashes in `source_map.json`.

The full 128-cell means and standard deviations remain machine-readable
repository evidence. They should not become a dense paper appendix table.

## Remove, merge, or demote

- **Remove from the proposed v2:** the old high-severity four-task heatmap plus
  rank-association composite. It asks the reader to decode two different claims
  at once.
- **Remove from the proposed v2:** the forced SIGReg-collapse result and its
  appendix table. Retain only the definition-level constant-representation
  counterexample in the method and discussion.
- **Do not promote:** the full 128-row table, seed-by-seed curves, hashes,
  manifests, run IDs, or recipe-debug history.
- **Replace:** the future-work sentence requesting multiple perturbation
  severities, because Gaussian severity is now evaluated explicitly.
- **Narrow:** any statement that the Boolean joint screen identifies high-severity
  failures. The current evidence establishes activation and continuous
  association, not selection utility.
- **Keep in the appendix:** exact association ranges and retention-ratio
  sensitivity.
- **Keep in repository documentation only:** the compatibility audit explaining
  why the old and new training grids are not concatenated.

## Main display

Use a single stacked bar chart. Every bar contains the same 96
task-by-training-run-by-training-strength rows. The three segments show:

1. pass IR and SR;
2. pass IR but fail SR;
3. fail IR.

This is more legible than a task heatmap or a Spearman plot. It directly shows
that the SR-veto fraction among IR-passing rows is small at low evaluation
severity and larger in harder slices. Its caption must also say that the
counts are descriptive and do not measure checkpoint-selection accuracy.
