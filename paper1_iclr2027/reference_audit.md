# ICLR 2027 reference audit

## Current integration check — 2026-09-16

The approved `preview_20260914/writing_preview.tex` has been promoted unchanged
to `main.tex`; the preview remains available. A full TeX Live 2025 build
(LaTeX, BibTeX, LaTeX twice) generated `build/main.pdf` and synchronized
`main.pdf`. The build script now performs that synchronization automatically.

- The current auxiliary file cites 44 unique keys and the rendered bibliography
  contains 44 entries. The main and preview `.bbl` files are identical.
- `references.bib` contains 61 entries; 17 inventory entries are not rendered.
- Both the pre-promotion main bibliography and the preview already contained
  44 entries. The discrepancy with the 41-entry report below is a stale audit
  record, not a new citation loss caused by promotion.
- VICReg (`bardes2022vicreg`), LeJEPA (`balestriero2025lejepa`), and VISReg
  (`wu2026visreg`) are present in the current bibliography. They are not
  covered by the historical 41-entry scope below.
- Main text ends on page 9; statements and references begin on page 10;
  Appendix A, now titled **Proofs**, begins on page 13. The PDF has 24 pages.
- The final LaTeX pass has no undefined citations/references, duplicate-label
  warnings, overfull boxes, or rerun request. BibTeX completed successfully.
- PLDM details are in Appendix C, blur/resize details in Appendix G, and
  Appendix I is **Adaptive-CEM Selection Regret**. Historical statements below
  about a retained fixed-pool certificate analysis do not describe this version.

### Verification boundary and remaining author checks

This update verifies source/build integration, citation coverage, and output
consistency. It does **not** constitute a new publisher-level metadata audit
or a new scientific validation of every citation-to-claim relationship.
The historical audit below is retained for provenance, not re-certified.
Its publication-status checks and the recorded page-range discrepancy still
require author review; the three additional works above also need to be
included in any renewed external-source audit. No bibliography metadata,
experimental data, or approved manuscript wording was changed in this promotion.

## Historical audit — 2026-09-04 (superseded counts and layout)

The remainder records the earlier version only. References to "current",
"final", 41 entries, and fixed-pool sections below refer to that historical
snapshot and must not be read as the status of the promoted manuscript.

Checked on 2026-09-04 against the current `main.tex`, `references.bib`, the
rendered `build/main.bbl`, earlier manuscript versions, and primary publisher,
proceedings, project, and arXiv records.

## Final scope and result

- The manuscript contains 37 citation commands, 51 cited-key occurrences, and
  41 unique cited works.
- `main.tex` and `build/main.bbl` contain exactly the same 41 keys. There are no
  undefined citations, missing rendered entries, or extra rendered entries.
- `references.bib` contains 58 entries. The 17 entries not cited by the final
  manuscript are retained only as a working related-work inventory and are not
  rendered by BibTeX.
- The earlier attempt to preserve all 58 citations required a standalone
  Additional Related Work appendix. That section was removed because it did
  not fit the paper's narrative. The final 41-work selection keeps the closest
  lineage, robustness, diagnostic, and certificate literature in the main
  Related Work section.
- Titles, authors, years, venues/publication types, page ranges where
  applicable, and DOI/URL identifiers of the 41 rendered works were checked
  against primary records. No evident citation-to-claim mismatch remains.
- The appendix t-SNE analysis continues to cite
  `vandermaaten2008tsne`; its entry is rendered normally.

## URL and DOI policy

ICLR 2027 requires the official bibliography style, but does not require links
to have uniform visual lengths. The bibliography uses a source-type policy:

- use a DOI for a formally published paper when a stable DOI is available;
- otherwise use the canonical OpenReview, PMLR/JMLR, conference, project, or
  arXiv record;
- do not retain both DOI and URL for one entry because the official ICLR `.bst`
  prints both and would create redundant links.

The 41 rendered entries contain 9 DOI fields and 32 canonical HTTPS URL fields.
Long and short links therefore reflect source type rather than inconsistent
formatting. The final bibliography has no underfull or overfull hbox.

## Bibliography normalization already applied

| Key | Change | Primary evidence |
|---|---|---|
| `ghaemi2025seqjepa` | Replaced the long NeurIPS proceedings URL with DOI `10.52202/085713-1104`. | The official NeurIPS 2025 BibTeX confirms title, authors, volume, pages, year, and DOI. |
| `vanassel2025jointembeddingreconstruction` | Replaced the long NeurIPS proceedings URL with DOI `10.52202/085713-0740`. | The official NeurIPS 2025 BibTeX confirms title, authors, volume, pages, year, and DOI. |
| `bsmpc` | Replaced the long `proceedings.iclr.cc` URL with `https://openreview.net/forum?id=F07ic7huE3`. | The OpenReview record identifies the ICLR 2025 paper and its authors. |

No entry in `references.bib` was invented or changed during the final
main-versus-appendix reallocation.

## Final Related Work selection

- World-model and JEPA lineage: DreamerV3, TD-MPC2, core JEPA work, LeWM,
  PLDM, self-predictive collapse, action conditioning, retained features, and
  seq-JEPA.
- Visual robustness: DrQ/DrQ-v2/SODA, ReOI, DreamerPro, Denoised MDPs, latent
  dynamic robust representations, bisimulation, and MWM.
- Diagnostics and guarantees: intended-use evaluation, ATM, CARRL/CROP,
  action-content and rollout/model-error diagnostics, WMAttack, and ARB4WM.

The following 17 database entries are intentionally not cited in the final
manuscript:

`dupuis2023vibr`, `fu2021tia`, `grimm2020valueequivalence`, `guo2020pbl`,
`hutson2024policyshaped`, `klindt2026lejepaworldmodel`, `nguyen2021tpc`,
`pan2022isodream`, `ruan2026futurecompatible`, `schwarzer2021spr`,
`seo2026acid`, `sobal2022jointembeddingpredictivearchitectures`, `vigmo`,
`voelcker2025calibratedvalueaware`, `wang2024ad3`, `wang2026groupactions`, and
`zhang2026deltajepa`.

They were omitted because they are more distant training objectives,
alternative abstractions, or overlapping examples already represented by more
direct works. They should not be reinserted merely to increase the reference
count.

## Citation-to-claim verification

- ReOI is described as a test-time observation intervention for distractor
  sensitivity; DreamerPro uses prototype prediction; Denoised MDPs retain
  controllable, reward-relevant information; and Sun et al. combine temporal
  masking with bisimulation.
- ATM compares action information in encoded and predicted transitions.
  WMAttack searches for visual attacks on world-model agents, whereas ARB4WM
  targets policy, value, and latent-dynamics components.
- The main-text contrast retains the necessary scope: MWM enforces rollout
  consistency during training, while ACPC measures clean--perturbed divergence
  in a frozen model under the same actions. The diagnostic paragraph also
  retains intended-use evaluation, the evaluated-pair/fixed-pool restriction,
  and the fact that ACPC does not require the true future.
- Existing citations continue to support CEM, t-SNE, Jacobian Frobenius
  sensitivity, and the Hutchinson trace estimator.

## Items to recheck manually before submission

1. Recheck publication status and latest metadata for the cited fast-moving
   preprints: `assran2025vjepa2`, `maes2026lewm`, `toso2026bisimjepa`,
   `yan2026mwm`, `yu2026worldmodelevaluation`, `chen2026atm`,
   `guo2026wmattack`, `schaefer2026kinematic`, `yeom2026actionrelevant`,
   `vakalis2026operator`, `you2026controlpredictability`, and
   `zhang2026arb4wm`.
2. Decide whether to keep the official NeurIPS page range for
   `vanassel2025jointembeddingreconstruction`. The NeurIPS paper page and its
   official BibTeX report 21897--21937, while Crossref reports 24862--24902.
   The manuscript currently follows the NeurIPS primary record.
3. Read the final three Related Work paragraphs once for authorial emphasis.
   Their wording, claim matching, and transitions pass independent review, but
   the relative emphasis among concurrent works is ultimately an editorial
   choice.
4. Prune the 17 unused inventory entries when producing a clean submission-only
   source bundle, or leave them in the working repository if future reuse is
   desired. They do not appear in the PDF.

## Build verification

- Built successfully with `/opt/texlive/2025/bin/x86_64-linux` and the local
  official ICLR 2027 `.sty`/`.bst` files.
- No LaTeX error, undefined citation/reference, BibTeX warning, overfull hbox,
  underfull hbox, or multiply defined label remains. Benign underfull vbox
  notices do not affect content or the page limit.
- The main-text end label is on page 9. AI use, reproducibility, and References
  start on page 10. Appendix A now begins with Proofs and Fixed-Pool Analysis on
  page 13. The complete PDF has 24 pages.
- The abstract was not edited during this reallocation.

## Batch-agent note

The exact user-authorized Claude wrapper was previously invoked with Opus and
xhigh. Full-document tool-use sessions either stalled without output or parsed
only a prompt fragment, so no incomplete Claude response was treated as an
audit. The writing reallocation was performed by Sol medium and then checked by
the main Sol process and an independent read-only Sol audit.
